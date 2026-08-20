"""AI Painter — local SD-Turbo emotion/surface polish (Mandala Visual Body).

Status: **partial_with_gaps**. Uses bridge :13305 → sd-server :13306 on RX 580.
Not photoreal. Not Cosmos. No NVIDIA API keys.
Offline / bridge-down paths return beauty_skipped_* and never claim a beauty pass.
"""

from __future__ import annotations

import base64
import json
import os
import shutil
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

try:
    from nce.canonical import file_sha256
except ImportError:  # pragma: no cover
    from canonical import file_sha256  # type: ignore


STATUS_PARTIAL_WITH_GAPS = "partial_with_gaps"

GAPS_BASE = [
    "photoreal_not_guaranteed",
    "emotion_layer_only_not_anatomy_replace",
    "rx580_512_path_only_no_1024_oom_safe",
]

GAPS_APPLIED = GAPS_BASE + [
    "txt2img_not_img2img_locked_to_keyframe",
]

GAPS_SKIPPED = GAPS_BASE + [
    "beauty_pass_not_executed",
]


def lemonade_base_url() -> str:
    explicit = os.environ.get("LEMONADE_API_BASE", "").strip()
    if explicit:
        return explicit.rstrip("/")
    host = os.environ.get("LEMONADE_HOST", "").strip() or "127.0.0.1"
    port = os.environ.get("LEMONADE_PORT", "").strip() or "13305"
    return f"http://{host}:{port}/api/v1"


def probe_bridge(timeout_s: float = 2.5) -> dict[str, Any]:
    base = lemonade_base_url()
    origin = base.replace("/api/v1", "").rstrip("/")
    url = f"{origin}/health"
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout_s) as res:
            return {"ok": 200 <= res.status < 300, "origin": origin, "status": res.status}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "origin": origin, "status": 0, "error": str(exc)[:120]}


def _write_png_from_b64(dest: Path, b64: str) -> str:
    raw = base64.b64decode(b64)
    if raw[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("response is not a PNG")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(raw)
    return file_sha256(dest)


def _skipped(
    *,
    keyframe: Path,
    dest: Path,
    beauty_status: str,
    bridge: dict[str, Any] | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    shutil.copy2(keyframe, dest)
    out: dict[str, Any] = {
        "painterStatus": STATUS_PARTIAL_WITH_GAPS,
        "beautyStatus": beauty_status,
        "modelIds": [],
        "uri": str(dest),
        "sha256": file_sha256(dest),
        "source": "copy",
        "gaps": list(GAPS_SKIPPED),
        "claim": "not_photoreal_copy_fallback",
    }
    if bridge is not None:
        out["bridge"] = bridge
    if error:
        out["error"] = error
    return out


def paint_keyframe(
    keyframe: Path,
    dest: Path,
    *,
    prompt: str,
    dry_run: bool = False,
    disabled: bool = False,
) -> dict[str, Any]:
    """Optional SD-Turbo painter pass. Returns beautyStatus + modelIds + sha256 + gaps."""
    keyframe = Path(keyframe).resolve()
    dest = Path(dest).resolve()
    dest.parent.mkdir(parents=True, exist_ok=True)

    if dry_run:
        return _skipped(
            keyframe=keyframe,
            dest=dest,
            beauty_status="beauty_skipped_dry_run",
        )

    if disabled or os.environ.get("NCE_BEAUTY_POLISH", "1") == "0":
        return _skipped(
            keyframe=keyframe,
            dest=dest,
            beauty_status="beauty_skipped_disabled",
        )

    health = probe_bridge()
    if not health.get("ok"):
        return _skipped(
            keyframe=keyframe,
            dest=dest,
            beauty_status="beauty_skipped_bridge_down",
            bridge=health,
        )

    base = lemonade_base_url()
    timeout_ms = int(os.environ.get("NCE_BEAUTY_TIMEOUT_MS", "60000"))
    payload = {
        "model": "SD-Turbo",
        "prompt": prompt,
        "size": "512x512",
        "steps": 4,
        "response_format": "b64_json",
    }
    headers = {"Content-Type": "application/json"}
    key = os.environ.get("LEMONADE_API_KEY", "").strip()
    if key:
        headers["Authorization"] = f"Bearer {key}"

    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{base}/images/generations",
        data=body,
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_ms / 1000.0) as res:
            data = json.loads(res.read().decode("utf-8"))
        b64 = (data.get("data") or [{}])[0].get("b64_json")
        if not b64:
            raise ValueError("missing b64_json")
        sha = _write_png_from_b64(dest, b64)
        return {
            "painterStatus": STATUS_PARTIAL_WITH_GAPS,
            "beautyStatus": "beauty_applied_sd_turbo",
            "modelIds": ["SD-Turbo"],
            "uri": str(dest),
            "sha256": sha,
            "source": "lemonade_generations",
            "bridge": health,
            "gaps": list(GAPS_APPLIED),
            "claim": "emotion_surface_layer_not_photoreal",
        }
    except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
        return _skipped(
            keyframe=keyframe,
            dest=dest,
            beauty_status="beauty_skipped_bridge_down",
            bridge=health,
            error=str(exc)[:160],
        )
