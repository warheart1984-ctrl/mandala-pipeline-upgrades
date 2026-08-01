"""Pre-render demo frames → local + B2 with provenance sidecars.

Spread gens across a 24h window with ``--sleep-seconds`` / ``--schedule-hint``.
Uses GMI Cloud (GenBlaze SDK) when available; otherwise fal / NVIDIA / hfspace
via the polish cascade is **not** used for T2I — fall back to dry local
placeholder only when ``--allow-placeholder``.

Usage (from ``mrs/apps/genblaze-media``)::

  python -m app.pre_render --shot-id mandala-open --frames 0-23 \\
    --prompt "cel-shaded mandala oracle mask, anime look" \\
    --sleep-seconds 3600 --upload-b2

  # Or shot plan JSON:
  python -m app.pre_render --plan plans/demo-shot-plan.json --upload-b2

Status: **partial** — scheduling + B2 layout enforced; live gens need GMI credits.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any

from app.config import get_settings
from app.demo_cache import (
    SOURCE_LIVE_GENERATE,
    build_frame_provenance,
    cache_frame_key,
    sha256_bytes,
    upload_frame_to_b2,
    write_local_sidecars,
)
from app.gmi_provider import (
    GmiError,
    GmiNotConfiguredError,
    generate_image_gmi,
    gmi_availability,
)
from app.provider_cascade import cascade_health

logger = logging.getLogger(__name__)


def _parse_frame_range(spec: str) -> list[int]:
    """Parse ``0-23`` or ``0,1,2`` or ``5`` into frame indices."""
    spec = (spec or "").strip()
    if not spec:
        raise ValueError("empty frame spec")
    frames: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            start, end = int(a), int(b)
            if end < start:
                raise ValueError(f"bad range {part}")
            frames.extend(range(start, end + 1))
        else:
            frames.append(int(part))
    return frames


def _load_plan(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("plan must be a JSON object")
    return data


def _tiny_png() -> bytes:
    """1×1 PNG placeholder for offline dry scheduling tests."""
    import struct
    import zlib

    def chunk(t: bytes, d: bytes) -> bytes:
        c = t + d
        crc = struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
        return struct.pack(">I", len(d)) + c + crc

    raw = b"\x00\xff\x00\x00\xff"
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw))
        + chunk(b"IEND", b"")
    )


def schedule_hint(frame_count: int, window_hours: float = 24.0) -> dict[str, Any]:
    """Suggest sleep between frames to spread work across a wall-clock window."""
    if frame_count <= 0:
        return {"sleep_seconds": 0, "window_hours": window_hours, "frames": 0}
    total = window_hours * 3600.0
    sleep = total / frame_count if frame_count else 0
    return {
        "sleep_seconds": round(sleep, 1),
        "window_hours": window_hours,
        "frames": frame_count,
        "note": (
            f"Sleep ~{sleep:.0f}s between frames to spread {frame_count} gens "
            f"across {window_hours:g}h (rate-limit friendly)."
        ),
    }


def render_one_frame(
    settings: Any,
    *,
    shot_id: str,
    frame: int,
    prompt: str,
    out_root: Path,
    upload_b2: bool,
    allow_placeholder: bool,
    anime_world_profile_id: str | None,
    provider_preference: str,
) -> dict[str, Any]:
    """Generate one frame, write sidecars, optional B2 upload."""
    image_bytes: bytes | None = None
    provider = "placeholder"
    model = None
    detail = None

    if provider_preference in ("gmi", "auto"):
        try:
            result = generate_image_gmi(settings, prompt)
            image_bytes = result.image_bytes
            provider = result.provider
            model = result.model
            detail = result.detail
        except (GmiNotConfiguredError, GmiError) as exc:
            logger.warning("GMI frame %s/%s failed: %s", shot_id, frame, exc)
            if provider_preference == "gmi" and not allow_placeholder:
                raise

    if image_bytes is None:
        if not allow_placeholder:
            raise RuntimeError(
                "No image provider succeeded. Set GMI_API_KEY + install "
                "genblaze-gmicloud, or pass --allow-placeholder for dry layout tests."
            )
        image_bytes = _tiny_png()
        provider = "placeholder"
        detail = "placeholder PNG (not live beauty)"

    digest = sha256_bytes(image_bytes)
    prov = build_frame_provenance(
        source=SOURCE_LIVE_GENERATE,
        shot_id=shot_id,
        frame=frame,
        asset_sha256=digest,
        storage_prefix=settings.storage_prefix,
        provider=provider,
        model=model,
        prompt=prompt,
        anime_world_profile_id=anime_world_profile_id,
        detail=detail,
    )
    frame_dir = out_root / shot_id / f"f{frame:04d}"
    paths = write_local_sidecars(frame_dir, image_bytes, prov)
    uploaded: dict[str, Any] | None = None
    if upload_b2:
        uploaded = upload_frame_to_b2(settings, image_bytes, prov)

    return {
        "shot_id": shot_id,
        "frame": frame,
        "provider": provider,
        "model": model,
        "asset_sha256": digest,
        "local_render": str(paths["render"]),
        "local_manifest": str(paths["manifest"]),
        "b2": uploaded,
        "asset_key": cache_frame_key(settings.storage_prefix, shot_id, frame),
        "source": SOURCE_LIVE_GENERATE,
    }


def run_pre_render(args: argparse.Namespace) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    settings = get_settings()
    out_root = Path(args.out_dir).resolve()
    out_root.mkdir(parents=True, exist_ok=True)

    jobs: list[dict[str, Any]] = []
    if args.plan:
        plan = _load_plan(Path(args.plan))
        shot_id = plan.get("shot_id") or args.shot_id
        prompt = plan.get("prompt") or args.prompt
        frames = plan.get("frames")
        if isinstance(frames, str):
            frame_list = _parse_frame_range(frames)
        elif isinstance(frames, list):
            frame_list = [int(f) for f in frames]
        else:
            frame_list = _parse_frame_range(args.frames)
        anime_id = plan.get("anime_world_profile_id") or args.anime_world_profile_id
        for fr in frame_list:
            p = plan.get("prompts", {}).get(str(fr), prompt) if isinstance(plan.get("prompts"), dict) else prompt
            jobs.append(
                {
                    "shot_id": shot_id,
                    "frame": fr,
                    "prompt": p,
                    "anime_world_profile_id": anime_id,
                }
            )
    else:
        if not args.shot_id or not args.prompt:
            logger.error("--shot-id and --prompt required (or --plan)")
            return 2
        for fr in _parse_frame_range(args.frames):
            jobs.append(
                {
                    "shot_id": args.shot_id,
                    "frame": fr,
                    "prompt": args.prompt,
                    "anime_world_profile_id": args.anime_world_profile_id,
                }
            )

    hint = schedule_hint(len(jobs), window_hours=float(args.window_hours))
    sleep_s = float(args.sleep_seconds) if args.sleep_seconds is not None else hint["sleep_seconds"]
    if args.schedule_hint_only:
        print(json.dumps({"schedule": hint, "jobs": len(jobs), "cascade": cascade_health(settings)}, indent=2))
        return 0

    logger.info(
        "pre-render %d frames · sleep=%.1fs · upload_b2=%s · gmi=%s",
        len(jobs),
        sleep_s,
        args.upload_b2,
        gmi_availability(settings).get("available"),
    )
    results: list[dict[str, Any]] = []
    for i, job in enumerate(jobs):
        logger.info("frame %s/%s (%d/%d)", job["shot_id"], job["frame"], i + 1, len(jobs))
        row = render_one_frame(
            settings,
            shot_id=job["shot_id"],
            frame=int(job["frame"]),
            prompt=str(job["prompt"]),
            out_root=out_root,
            upload_b2=bool(args.upload_b2),
            allow_placeholder=bool(args.allow_placeholder),
            anime_world_profile_id=job.get("anime_world_profile_id"),
            provider_preference=args.provider,
        )
        results.append(row)
        if i + 1 < len(jobs) and sleep_s > 0:
            logger.info("sleeping %.1fs (24h-window batching)", sleep_s)
            time.sleep(sleep_s)

    summary = {
        "status": "ok",
        "frames": len(results),
        "schedule": hint,
        "sleep_seconds_used": sleep_s,
        "results": results,
        "b2_prefix": f"{settings.storage_prefix}/demo-cache/",
        "cascade": cascade_health(settings),
    }
    summary_path = out_root / "pre-render-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({"summary": str(summary_path), "frames": len(results)}, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Pre-render GenBlaze demo frames to B2")
    p.add_argument("--plan", help="JSON shot plan path")
    p.add_argument("--shot-id", help="Shot id (e.g. mandala-open)")
    p.add_argument("--frames", default="0", help="Frame range: 0-23 or 0,1,2")
    p.add_argument("--prompt", help="T2I prompt for all frames (unless plan overrides)")
    p.add_argument(
        "--out-dir",
        default="../../../tmp/genblaze-demo-cache",
        help="Local output root for PNG + manifest sidecars",
    )
    p.add_argument("--upload-b2", action="store_true", help="Upload each frame to B2")
    p.add_argument(
        "--sleep-seconds",
        type=float,
        default=None,
        help="Sleep between frames (default: spread across --window-hours)",
    )
    p.add_argument("--window-hours", type=float, default=24.0, help="Spread window")
    p.add_argument(
        "--schedule-hint-only",
        action="store_true",
        help="Print suggested sleep; do not generate",
    )
    p.add_argument(
        "--allow-placeholder",
        action="store_true",
        help="Write tiny PNG when GMI unavailable (layout/dry tests only)",
    )
    p.add_argument(
        "--provider",
        default="auto",
        choices=("auto", "gmi"),
        help="Image provider (GMI via GenBlaze SDK)",
    )
    p.add_argument("--anime-world-profile-id", default=None)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return run_pre_render(args)
    except Exception as exc:  # noqa: BLE001
        logger.error("%s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
