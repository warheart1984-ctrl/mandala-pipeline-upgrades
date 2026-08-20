#!/usr/bin/env python3
"""NCE demo pipeline — Story truth refs → AI Painter → Simulation Chamber → NCS.

Honest: no Cosmos, no Story Forge rebuild, no full reconstruction/physics.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aais import planned_worker_ids_for_request, worker_stub_manifest
from ai_painter import paint_keyframe, probe_bridge
from mythar import accept_audio_plan
from nce import CAPABILITY_ID, SCHEMA_VERSION
from nce.canonical import file_sha256
from nce.validate import (
    NceContractError,
    validate_ncs,
    validate_request,
    validate_scw,
    validate_srp,
)
from simulation_chamber import run_chamber, solid_png


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def ensure_keyframe(path: Path | None, fixtures: Path) -> Path:
    if path and path.is_file():
        return path.resolve()
    try:
        fixtures.mkdir(parents=True, exist_ok=True)
        dest = fixtures / "keyframe-64.png"
        dest.write_bytes(solid_png(64, 64, (48, 72, 120)))
        return dest.resolve()
    except OSError:
        # Worktree / sandbox may deny writes under package fixtures/
        fallback = Path("/tmp/nce-fixtures")
        fallback.mkdir(parents=True, exist_ok=True)
        dest = fallback / "keyframe-64.png"
        dest.write_bytes(solid_png(64, 64, (48, 72, 120)))
        return dest.resolve()


def stub_srp(source_image: Path) -> dict:
    return {
        "schemaVersion": SCHEMA_VERSION,
        "kind": "SceneReconstructionPackage",
        "status": "declared_stub",
        "capabilityId": CAPABILITY_ID,
        "sourceImageRef": str(source_image),
        "depthRef": None,
        "normalsRef": None,
        "segmentationRef": None,
        "camera": None,
        "limitation": (
            "Photo→SRP reconstruction is declared_stub — no monocular depth, "
            "normals, segmentation, or mesh in this scaffold."
        ),
        "gaps": [
            "no_monocular_depth",
            "no_normals",
            "no_segmentation",
            "no_mesh_reconstruction",
            "no_camera_solve",
        ],
    }


def build_request(args: argparse.Namespace, keyframe: Path) -> dict:
    req = {
        "schemaVersion": SCHEMA_VERSION,
        "kind": "NeuralCinematicRequest",
        "capabilityId": CAPABILITY_ID,
        "style": args.style,
        "emotion_intensity": float(args.emotion_intensity),
        "requires_simulation": True,
        "baseKeyframePath": str(keyframe),
        "shotSpec": {
            "cameraPathId": args.camera_path,
            "mood": args.mood,
            "weatherTags": [t for t in args.weather.split(",") if t.strip()] if args.weather else [],
            "frameCount": int(args.frames),
        },
        "productionId": args.production_id,
        "sceneId": args.scene_id,
        "characterId": args.character_id or None,
        "identityLock": None,
        "audioPlan": None,
        "dryRun": bool(args.dry_run),
    }
    if args.character_id and args.species:
        req["identityLock"] = {
            "species": args.species,
            "faceRefId": args.face_ref or "face-ref-declared",
            "bodyBuild": args.body_build or "medium",
            "armorId": args.armor_id or "none",
            "weaponId": args.weapon_id or "none",
            "weaponHeldIn": "none",
        }
    if args.score_identity:
        req["audioPlan"] = {
            "scoreIdentity": args.score_identity,
            "statusTag": "declared",
            "mappingStatusTag": "partial",
            "cues": [],
        }
    return req


def run_demo(args: argparse.Namespace) -> dict:
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    run_dir = out / f"nce-run-{_utc_stamp()}"
    run_dir.mkdir(parents=True, exist_ok=True)

    keyframe = ensure_keyframe(
        Path(args.keyframe) if args.keyframe else None,
        ROOT / "fixtures",
    )
    # Never invent characterId from keyframe basename
    request = build_request(args, keyframe)
    validate_request(request)

    srp = stub_srp(keyframe)
    validate_srp(srp)
    (run_dir / "srp.declared_stub.json").write_text(
        json.dumps(srp, indent=2) + "\n", encoding="utf-8"
    )

    prompt = (
        f"{request['style']} cinematic still, mood={request['shotSpec'].get('mood')}, "
        f"emotion_intensity={request['emotion_intensity']}. "
        "Same identity and proportions. Emotion/surface layer only — not a new character."
    )
    painted = paint_keyframe(
        keyframe,
        run_dir / "01-painted.png",
        prompt=prompt,
        dry_run=bool(args.dry_run),
        disabled=bool(args.no_paint),
    )

    scw, frames = run_chamber(
        out_dir=run_dir / "sim_frames",
        base_still=Path(painted["uri"]),
        production_id=request["productionId"] or "nce-demo-production",
        scene_id=request["sceneId"] or "nce-demo-scene",
        shot_spec=request["shotSpec"],
        character_id=request.get("characterId"),
        identity_lock=request.get("identityLock"),
        weather_intent=request["shotSpec"].get("weatherTags"),
        emotional_vector={
            "emotion_intensity": request["emotion_intensity"],
            "mood": request["shotSpec"].get("mood"),
        },
    )
    validate_scw(scw)
    (run_dir / "scw.json").write_text(json.dumps(scw, indent=2) + "\n", encoding="utf-8")

    mythar_ref = accept_audio_plan(request.get("audioPlan"))
    workers = planned_worker_ids_for_request(
        requires_simulation=True,
        paint=painted.get("beautyStatus") == "beauty_applied_sd_turbo",
    )

    still_refs = [
        {
            "role": "base_keyframe",
            "uri": str(keyframe),
            "sha256": file_sha256(keyframe),
            "notes": "input keyframe (fixture or operator path)",
        },
        {
            "role": "beauty" if painted["beautyStatus"] == "beauty_applied_sd_turbo" else "copy_fallback",
            "uri": painted["uri"],
            "sha256": painted["sha256"],
            "notes": painted["beautyStatus"],
        },
        *[{k: v for k, v in fr.items() if k != "buffers"} for fr in frames],
    ]

    model_ids = list(painted.get("modelIds") or []) + [
        "simulation_chamber.camera_orbit_flipbook"
    ]
    ncs_gaps = [
        "not_movie_lane_assemble",
        "simulation_chamber_ken_burns_not_true_3d",
        "srp_declared_stub",
        "cosmos_skipped_local",
        "mythar_audio_declared_only",
    ]
    if painted.get("painterStatus") == "partial_with_gaps":
        ncs_gaps.extend(painted.get("gaps") or ["ai_painter_partial_with_gaps"])
    ncs = {
        "schemaVersion": SCHEMA_VERSION,
        "kind": "NeuralCinematicSequence",
        "status": "partial_with_gaps",
        "capabilityId": CAPABILITY_ID,
        "sequenceId": f"ncs-{run_dir.name}",
        "productionId": scw["productionId"],
        "sceneId": scw["sceneId"],
        "clipMetadata": {
            "label": "nce-simulation-chamber-flipbook",
            "frameCount": len(frames),
            "fps": float(args.fps),
            "motionBackend": "camera_orbit_flipbook",
        },
        "stillRefs": still_refs,
        "frameRefs": [
            {
                "index": i,
                "uri": fr["uri"],
                "sha256": fr["sha256"],
                "camera": fr["camera"],
            }
            for i, fr in enumerate(frames)
        ],
        "modelIds": model_ids,
        "beautyStatus": painted["beautyStatus"],
        "gaps": ncs_gaps,
        "provenance": {
            "intentId": args.intent_id or f"intent-{run_dir.name}",
            "worldId": args.world_id or scw["sceneId"],
            "timelineId": args.timeline_id or "timeline-nce-demo",
            "capabilityId": CAPABILITY_ID,
            "modelIds": model_ids,
            "artifactHashes": {
                "keyframe": file_sha256(keyframe),
                "painted": painted["sha256"],
                **{f"frame_{i:03d}": fr["sha256"] for i, fr in enumerate(frames)},
            },
            "limitation": (
                "partial_with_gaps stills + Simulation Chamber flipbook only. "
                "No Cosmos. No Movie Lane assemble. SRP declared_stub."
            ),
        },
        "mytharAudioRef": mythar_ref,
        "aaisWorkers": {
            "status": "declared",
            "plannedWorkerIds": workers,
            "manifest": worker_stub_manifest(),
        },
        "organs": {
            "storyForge": "boundary_only",
            "mandala": "this_package",
            "mythar": "declared_boundary",
            "aais": "declared_stubs",
            "simulationChamber": "partial_with_gaps",
            "cosmos": "declared_optional_skipped",
            "movieLaneAssemble": "declared_infinity",
        },
        "limitation": (
            "This NCS is a governed stills/flipbook package — not a finished movie, "
            "not Cosmos video paint, not physics world."
        ),
    }
    validate_ncs(ncs)
    ncs_path = run_dir / "ncs.json"
    ncs_path.write_text(json.dumps(ncs, indent=2) + "\n", encoding="utf-8")

    summary = {
        "runDir": str(run_dir),
        "ncsPath": str(ncs_path),
        "beautyStatus": painted["beautyStatus"],
        "painterStatus": painted.get("painterStatus"),
        "bridge": probe_bridge() if not args.dry_run else {"ok": False, "note": "dry_run"},
        "frameCount": len(frames),
        "cosmosRequired": False,
        "status": {
            "SRP": "declared_stub",
            "SCW": scw["status"],
            "NCS": ncs["status"],
            "SimulationChamber": scw["status"],
            "AIPainter": painted.get("painterStatus"),
            "Cosmos": "declared_optional_skipped",
        },
        "gaps": {
            "SRP": srp.get("gaps"),
            "SCW": scw.get("gaps"),
            "NCS": ncs.get("gaps"),
            "AIPainter": painted.get("gaps"),
        },
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Neural Cinematic Engine demo (partial, no Cosmos)")
    p.add_argument("--keyframe", default="", help="PNG/JPEG path (optional; fixture generated)")
    p.add_argument("--out-dir", default=str(ROOT / "outputs"))
    p.add_argument("--camera-path", default="orbit", choices=["push-in", "orbit", "close-up"])
    p.add_argument("--frames", type=int, default=8)
    p.add_argument("--fps", type=float, default=8.0)
    p.add_argument("--style", default="cinematic still")
    p.add_argument("--mood", default="tense")
    p.add_argument("--weather", default="")
    p.add_argument("--emotion-intensity", type=float, default=0.6)
    p.add_argument("--production-id", default="nce-demo-production")
    p.add_argument("--scene-id", default="nce-demo-scene")
    p.add_argument("--character-id", default="", help="From Story Forge — never from filename")
    p.add_argument("--species", default="")
    p.add_argument("--face-ref", default="")
    p.add_argument("--body-build", default="")
    p.add_argument("--armor-id", default="")
    p.add_argument("--weapon-id", default="")
    p.add_argument("--score-identity", default="", help="Mythar/Beatbox scoreIdentity hook")
    p.add_argument("--intent-id", default="")
    p.add_argument("--world-id", default="")
    p.add_argument("--timeline-id", default="")
    p.add_argument("--dry-run", action="store_true", help="Skip bridge; copy keyframe")
    p.add_argument("--no-paint", action="store_true", help="Force painter skip")
    args = p.parse_args(argv)

    try:
        summary = run_demo(args)
    except NceContractError as exc:
        print(f"NCE contract error: {exc}", file=sys.stderr)
        return 2

    print("============================================================")
    print(" NCE demo — Simulation Chamber (Cosmos NOT required)")
    print("============================================================")
    print("runDir=", summary["runDir"])
    print("ncs=", summary["ncsPath"])
    print("beautyStatus=", summary["beautyStatus"])
    print("painterStatus=", summary["painterStatus"])
    print("frames=", summary["frameCount"])
    print("cosmosRequired=", summary["cosmosRequired"])
    for k, v in summary["status"].items():
        print(f"  {k}: {v}")
    print("Movie Lane assemble = declared (Infinity / Story Forge) — not this package.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
