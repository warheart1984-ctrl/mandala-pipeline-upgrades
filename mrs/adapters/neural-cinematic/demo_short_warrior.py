#!/usr/bin/env python3
"""Warrior courtyard press-Play short via Story Forge contract + NCE Simulation Chamber.

Loads infinity-backend-build-warrior-courtyard.json → MandalaProductionRequest →
per-shot Simulation Chamber frames (identity-locked) → ffmpeg MP4.

Status: **partial_with_gaps** (fixture clay / Ken-Burns; not production sculpt;
click bed ≠ Beatbox score; Movie Lane assemble declared upstream).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ADAPTERS = ROOT.parent
BOUNDARY = ADAPTERS / "storyforge-boundary"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(BOUNDARY) not in sys.path:
    sys.path.insert(0, str(BOUNDARY))

from assemble import assemble_flipbook_mp4  # noqa: E402
from demo_pipeline import paint_keyframe, stub_srp  # noqa: E402
from nce import CAPABILITY_ID, SCHEMA_VERSION  # noqa: E402
from nce.canonical import file_sha256  # noqa: E402
from nce.validate import validate_ncs, validate_scw, validate_srp  # noqa: E402
from simulation_chamber import run_chamber, solid_png  # noqa: E402

from contract.map_infinity import (  # noqa: E402
    from_infinity_backend_build,
    to_mandala_production_request,
)
from contract.vertical_slice import compare_identity, emit_shot_artifacts  # noqa: E402
from contract.audio import compare_score_identity  # noqa: E402

FIXTURE = (
    BOUNDARY
    / "contract"
    / "fixtures"
    / "infinity-backend-build-warrior-courtyard.json"
)


def _camera_path_for_shot(shot: dict) -> str:
    move = str((shot.get("camera") or {}).get("move") or "").lower()
    if "push" in move or "dolly" in move or "crane" in move:
        return "push-in"
    if "close" in move or "intimate" in move:
        return "close-up"
    framing = str((shot.get("camera") or {}).get("lens") or "").lower()
    if "close" in framing or "85" in framing:
        return "close-up"
    if "wide" in framing or "24" in framing or "establishing" in move:
        return "orbit"
    return "orbit"


def _ensure_keyframe(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.is_file():
        # Distinct gunmetal-ish keyframe (fixture stand-in, not production clay PNG)
        path.write_bytes(solid_png(256, 256, (72, 78, 88)))
    return path


def run_warrior_short(
    *,
    out_dir: Path,
    dry_run: bool = True,
    frames_per_shot: int = 4,
    fps: float = 8.0,
) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = out_dir / f"warrior-short-{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    artifact = from_infinity_backend_build(raw)
    request = to_mandala_production_request(artifact)
    shots = emit_shot_artifacts(request)
    identity = compare_identity(shots[0], shots[-1])
    score = compare_score_identity(shots[0], shots[-1])
    if not identity.get("equal"):
        raise SystemExit(f"identity lock failed: {identity}")
    if not score.get("equal"):
        raise SystemExit(f"scoreIdentity lock failed: {score}")

    character = request["actors"][0]
    character_id = character["characterId"]
    identity_lock = character.get("identityLock")
    production_id = request["productionId"]
    scene_id = str(
        artifact.get("worldPack", {}).get("setting")
        or raw.get("scene_id")
        or "courtyard-approach"
    )
    score_identity = (request.get("audioPlan") or artifact.get("audioPlan") or {}).get(
        "scoreIdentity"
    )

    keyframe = _ensure_keyframe(run_dir / "warrior-keyframe.png")
    srp = stub_srp(keyframe)
    validate_srp(srp)
    (run_dir / "srp.declared_stub.json").write_text(
        json.dumps(srp, indent=2) + "\n", encoding="utf-8"
    )

    painted = paint_keyframe(
        keyframe,
        run_dir / "01-painted.png",
        prompt=(
            "gunmetal anthro fox warrior, orange eyes, grey studio, "
            "cinematic still, same identity — emotion layer only"
        ),
        dry_run=dry_run,
    )

    all_frame_paths: list[Path] = []
    shot_summaries: list[dict] = []
    for shot in request["shotTimeline"]:
        shot_id = shot["shotId"]
        camera_path = _camera_path_for_shot(shot)
        shot_dir = run_dir / "shots" / shot_id
        shot_spec = {
            "cameraPathId": camera_path,
            "mood": "courtyard-tense",
            "weatherTags": ["dust"],
            "frameCount": frames_per_shot,
        }
        scw, frames = run_chamber(
            out_dir=shot_dir,
            base_still=Path(painted["uri"]),
            production_id=production_id,
            scene_id=f"{scene_id}:{shot_id}",
            shot_spec=shot_spec,
            character_id=character_id,
            identity_lock=identity_lock,
            weather_intent=["dust"],
            emotional_vector={"shotId": shot_id, "action": shot.get("action")},
        )
        validate_scw(scw)
        (shot_dir / "scw.json").write_text(json.dumps(scw, indent=2) + "\n", encoding="utf-8")
        for fr in frames:
            all_frame_paths.append(Path(fr["uri"]))
        shot_summaries.append(
            {
                "shotId": shot_id,
                "cameraPathId": camera_path,
                "frameCount": len(frames),
                "characterId": character_id,
                "poseId": (shot.get("pose") or {}).get("id"),
            }
        )

    mp4_path = run_dir / "press-play.mp4"
    mux = assemble_flipbook_mp4(
        all_frame_paths,
        mp4_path,
        fps=fps,
        with_click=True,
    )

    still_refs = [
        {
            "role": "base_keyframe",
            "uri": str(keyframe),
            "sha256": file_sha256(keyframe),
            "notes": "warrior fixture keyframe stand-in",
        },
        {
            "role": "beauty" if painted["beautyStatus"] == "beauty_applied_sd_turbo" else "copy_fallback",
            "uri": painted["uri"],
            "sha256": painted["sha256"],
            "notes": painted["beautyStatus"],
        },
    ]
    for p in all_frame_paths:
        still_refs.append(
            {
                "role": "sim_frame",
                "uri": str(p),
                "sha256": file_sha256(p),
                "notes": "Simulation Chamber flipbook frame",
            }
        )

    ncs = {
        "schemaVersion": SCHEMA_VERSION,
        "kind": "NeuralCinematicSequence",
        "status": "partial_with_gaps",
        "capabilityId": CAPABILITY_ID,
        "sequenceId": f"ncs-warrior-{stamp}",
        "productionId": production_id,
        "sceneId": scene_id,
        "clipMetadata": {
            "label": "warrior-courtyard-press-play",
            "frameCount": len(all_frame_paths),
            "fps": fps,
            "motionBackend": "camera_orbit_flipbook",
            "shotCount": len(shot_summaries),
        },
        "stillRefs": still_refs,
        "frameRefs": [
            {"index": i, "uri": str(p), "sha256": file_sha256(p)}
            for i, p in enumerate(all_frame_paths)
        ],
        "modelIds": list(painted.get("modelIds") or [])
        + ["simulation_chamber.camera_orbit_flipbook", "ffmpeg.flipbook_mux"],
        "beautyStatus": painted["beautyStatus"],
        "gaps": [
            "fixture_clay_not_production_sculpt",
            "ken_burns_flipbook_not_true_3d",
            "click_bed_not_beatbox_score",
            "movie_lane_assemble_declared_infinity",
            "cosmos_skipped",
        ],
        "provenance": {
            "intentId": f"intent-warrior-{stamp}",
            "worldId": scene_id,
            "timelineId": "timeline-warrior-courtyard",
            "capabilityId": CAPABILITY_ID,
            "modelIds": list(painted.get("modelIds") or [])
            + ["simulation_chamber.camera_orbit_flipbook"],
            "artifactHashes": {
                "keyframe": file_sha256(keyframe),
                "painted": painted["sha256"],
                **{f"frame_{i:03d}": file_sha256(p) for i, p in enumerate(all_frame_paths)},
            },
            "limitation": (
                "Warrior press-Play short: Simulation Chamber flipbook + optional click. "
                "Identity S01==S08 enforced via storyforge-boundary. Not a finished film."
            ),
        },
        "mytharAudioRef": {
            "status": "declared",
            "scoreIdentity": score_identity,
            "gaps": ["beatbox_live_not_invoked", "click_fallback"],
        },
        "pressPlayMp4": mux.get("path") if mux.get("ok") else None,
        "organs": {
            "storyForge": "boundary_fixture_mapped",
            "simulationChamber": "partial_with_gaps",
            "aiPainter": painted.get("painterStatus"),
            "mythar": "declared",
            "movieLane": "declared",
            "cosmos": "declared_optional_skipped",
        },
        "limitation": (
            "partial_with_gaps press-Play flipbook — fixture warrior, not production sculpt; "
            "click ≠ score; Infinity Movie Lane not run."
        ),
    }
    validate_ncs(ncs)
    ncs_path = run_dir / "ncs.json"
    ncs_path.write_text(json.dumps(ncs, indent=2) + "\n", encoding="utf-8")

    summary = {
        "status": "partial_with_gaps",
        "runDir": str(run_dir),
        "pressPlayMp4": mux,
        "ncsPath": str(ncs_path),
        "productionId": production_id,
        "characterId": character_id,
        "scoreIdentity": score_identity,
        "identityCompare": identity,
        "scoreIdentityCompare": score,
        "shotSummaries": shot_summaries,
        "frameCount": len(all_frame_paths),
        "beautyStatus": painted["beautyStatus"],
        "cosmosRequired": False,
        "gaps": ncs["gaps"],
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Warrior courtyard NCE press-Play short")
    p.add_argument("--out-dir", default=str(ROOT / "outputs"))
    p.add_argument("--frames-per-shot", type=int, default=4)
    p.add_argument("--fps", type=float, default=8.0)
    p.add_argument("--dry-run", action="store_true", default=True)
    p.add_argument("--live-paint", action="store_true", help="Try SD-Turbo on :13305")
    args = p.parse_args(argv)
    dry = not bool(args.live_paint)
    summary = run_warrior_short(
        out_dir=Path(args.out_dir),
        dry_run=dry,
        frames_per_shot=int(args.frames_per_shot),
        fps=float(args.fps),
    )
    print("============================================================")
    print(" Warrior courtyard — press Play (Simulation Chamber)")
    print("============================================================")
    print("runDir=", summary["runDir"])
    print("characterId=", summary["characterId"])
    print("productionId=", summary["productionId"])
    print("scoreIdentity=", summary["scoreIdentity"])
    print("identityEqual=", summary["identityCompare"].get("equal"))
    print("scoreIdentityEqual=", summary["scoreIdentityCompare"].get("equal"))
    print("frames=", summary["frameCount"])
    mp4 = summary["pressPlayMp4"]
    if mp4.get("ok"):
        print("pressPlayMp4=", mp4["path"])
        print("tag=", mp4.get("tag"))
        print("bytes=", mp4.get("bytes"))
    else:
        print("pressPlayMp4 FAILED:", mp4.get("why", mp4)[:400])
        return 1
    print("status=", summary["status"])
    print("Cosmos = skipped (Simulation Chamber local path)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
