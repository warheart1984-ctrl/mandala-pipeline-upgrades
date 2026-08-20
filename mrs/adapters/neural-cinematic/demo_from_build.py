#!/usr/bin/env python3
"""Run NCE press-Play short from a Mandala-ready Story Forge --build-json.

Uses sculpt_under_lock keyframe when available (ZBrush production preview or
blender-anthro fixture preview — never claims ZBrush if mesh missing).
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from assemble import assemble_flipbook_mp4  # noqa: E402
from demo_pipeline import paint_keyframe, stub_srp  # noqa: E402
from infinity_bridge import map_build_to_mandala  # noqa: E402
from nce import CAPABILITY_ID, SCHEMA_VERSION  # noqa: E402
from nce.canonical import file_sha256  # noqa: E402
from nce.validate import validate_ncs, validate_scw, validate_srp  # noqa: E402
from sculpt_under_lock import resolve_sculpt_under_lock  # noqa: E402
from simulation_chamber import run_chamber, solid_png  # noqa: E402


def _camera_path_for_shot(shot: dict) -> str:
    move = str((shot.get("camera") or {}).get("move") or "").lower()
    if "push" in move or "dolly" in move:
        return "push-in"
    if "close" in move:
        return "close-up"
    return "orbit"


def run_from_build(
    *,
    build_json: Path,
    out_dir: Path,
    dry_run: bool = True,
    frames_per_shot: int = 3,
    fps: float = 6.0,
) -> dict:
    raw = json.loads(Path(build_json).read_text(encoding="utf-8"))
    mapped = map_build_to_mandala(raw)
    if not mapped["identityEqual"]:
        raise SystemExit(f"identity lock failed across shots: {mapped}")

    request = mapped["request"]
    actor = request["actors"][0]
    character_id = actor["characterId"]
    identity_lock = actor["identityLock"]
    production_id = request["productionId"]

    sculpt = resolve_sculpt_under_lock(character_id)
    # Prefer lock digests from sculpt resolve when production mesh present
    if sculpt.get("productionSculpt"):
        identity_lock = {**identity_lock, **sculpt["identityLock"]}

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = out_dir / f"from-build-{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    keyframe = run_dir / "sculpt-keyframe.png"
    if sculpt.get("keyframePath") and Path(sculpt["keyframePath"]).is_file():
        shutil.copy2(sculpt["keyframePath"], keyframe)
    else:
        keyframe.write_bytes(solid_png(256, 256, (72, 78, 88)))

    srp = stub_srp(keyframe)
    validate_srp(srp)
    (run_dir / "sculpt_resolve.json").write_text(
        json.dumps(sculpt, indent=2) + "\n", encoding="utf-8"
    )

    painted = paint_keyframe(
        keyframe,
        run_dir / "01-painted.png",
        prompt=(
            f"cinematic still of {character_id}, same identityLock proportions, "
            "emotion/surface layer only — do not invent anatomy"
        ),
        dry_run=dry_run,
    )

    frames_all: list[Path] = []
    for shot in request["shotTimeline"]:
        shot_id = shot["shotId"]
        path_id = _camera_path_for_shot(shot)
        scw, frames = run_chamber(
            out_dir=run_dir / "shots" / shot_id,
            base_still=Path(painted["uri"]),
            production_id=production_id,
            scene_id=f"{production_id}:{shot_id}",
            shot_spec={
                "cameraPathId": path_id,
                "mood": "cinematic",
                "weatherTags": [],
                "frameCount": frames_per_shot,
            },
            character_id=character_id,
            identity_lock=identity_lock,
        )
        validate_scw(scw)
        frames_all.extend(Path(fr["uri"]) for fr in frames)

    mux = assemble_flipbook_mp4(
        frames_all, run_dir / "press-play.mp4", fps=fps, with_click=True
    )

    still_refs = [
        {
            "role": "base_keyframe",
            "uri": str(keyframe),
            "sha256": file_sha256(keyframe),
            "notes": (
                "zbrush_production_preview"
                if sculpt.get("productionSculpt")
                else "fixture_or_blender_preview_not_zbrush"
            ),
        },
        {
            "role": "beauty"
            if painted["beautyStatus"] == "beauty_applied_sd_turbo"
            else "copy_fallback",
            "uri": painted["uri"],
            "sha256": painted["sha256"],
            "notes": painted["beautyStatus"],
        },
        *[
            {
                "role": "sim_frame",
                "uri": str(p),
                "sha256": file_sha256(p),
                "notes": "chamber",
            }
            for p in frames_all
        ],
    ]
    gaps = [
        "movie_lane_assemble_declared_infinity",
        "click_bed_not_beatbox",
        "cosmos_skipped",
    ]
    if sculpt.get("productionSculpt"):
        gaps.append("production_sculpt_partial_skin_rig_may_be_incomplete")
    else:
        gaps.append("zbrush_obj_missing_using_fixture_preview")

    ncs = {
        "schemaVersion": SCHEMA_VERSION,
        "kind": "NeuralCinematicSequence",
        "status": "partial_with_gaps",
        "capabilityId": CAPABILITY_ID,
        "sequenceId": f"ncs-from-build-{stamp}",
        "productionId": production_id,
        "sceneId": production_id,
        "stillRefs": still_refs,
        "modelIds": list(painted.get("modelIds") or [])
        + ["simulation_chamber.camera_orbit_flipbook"],
        "beautyStatus": painted["beautyStatus"],
        "gaps": gaps,
        "provenance": {
            "intentId": f"intent-from-build-{stamp}",
            "worldId": production_id,
            "timelineId": "timeline-from-build",
            "capabilityId": CAPABILITY_ID,
            "artifactHashes": {
                "keyframe": file_sha256(keyframe),
                **{f"f{i:03d}": file_sha256(p) for i, p in enumerate(frames_all)},
            },
            "limitation": (
                "From Story Forge build-json + sculpt_under_lock. "
                f"productionSculpt={sculpt.get('productionSculpt')}"
            ),
        },
        "pressPlayMp4": mux.get("path") if mux.get("ok") else None,
        "sculpt": {
            "productionSculpt": sculpt.get("productionSculpt"),
            "statusTag": sculpt.get("statusTag"),
            "meshPath": sculpt.get("meshPath"),
            "gaps": sculpt.get("gaps"),
        },
        "limitation": "partial_with_gaps press-Play from live/enriched SF build",
    }
    validate_ncs(ncs)
    ncs_path = run_dir / "ncs.json"
    ncs_path.write_text(json.dumps(ncs, indent=2) + "\n", encoding="utf-8")
    summary = {
        "status": "partial_with_gaps",
        "runDir": str(run_dir),
        "ncsPath": str(ncs_path),
        "pressPlayMp4": mux,
        "productionId": production_id,
        "characterId": character_id,
        "identityEqual": mapped["identityEqual"],
        "scoreIdentityEqual": mapped["scoreIdentityEqual"],
        "productionSculpt": sculpt.get("productionSculpt"),
        "sculptStatus": sculpt.get("statusTag"),
        "buildJson": str(Path(build_json).resolve()),
        "gaps": gaps,
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="NCE demo from Story Forge --build-json")
    p.add_argument("--build-json", required=True)
    p.add_argument("--out-dir", default=str(ROOT / "outputs"))
    p.add_argument("--frames-per-shot", type=int, default=3)
    p.add_argument("--fps", type=float, default=6.0)
    p.add_argument("--live-paint", action="store_true")
    args = p.parse_args(argv)
    summary = run_from_build(
        build_json=Path(args.build_json),
        out_dir=Path(args.out_dir),
        dry_run=not args.live_paint,
        frames_per_shot=args.frames_per_shot,
        fps=args.fps,
    )
    print("============================================================")
    print(" From Story Forge build-json → press Play")
    print("============================================================")
    print("buildJson=", summary["buildJson"])
    print("characterId=", summary["characterId"])
    print("productionSculpt=", summary["productionSculpt"])
    print("sculptStatus=", summary["sculptStatus"])
    print("identityEqual=", summary["identityEqual"])
    if summary["pressPlayMp4"].get("ok"):
        print("pressPlayMp4=", summary["pressPlayMp4"]["path"])
    else:
        print("mp4 failed:", summary["pressPlayMp4"])
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
