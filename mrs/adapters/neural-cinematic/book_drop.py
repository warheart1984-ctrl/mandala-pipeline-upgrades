"""Book drop bridge — markdown chapter → BackendBuildArtifact-shaped JSON → NCE.

Status: **partial_with_gaps**. This is a Mandala-side **heuristic** so operators can
demo book→flipbook before Infinity Movie Lane is fully driven from Linux.
It does **not** replace Story Forge narrative law. Identity must be supplied
explicitly (never invented from the filename).

For production: run Infinity Story Forge Movie Lane and pass the emitted JSON
into `infinity_bridge.map_build_to_mandala` / `demo_book_drop.py --build-json`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from infinity_bridge import map_build_to_mandala  # noqa: E402
from assemble import assemble_flipbook_mp4  # noqa: E402
from demo_pipeline import paint_keyframe, stub_srp  # noqa: E402
from nce import CAPABILITY_ID, SCHEMA_VERSION  # noqa: E402
from nce.canonical import file_sha256  # noqa: E402
from nce.validate import validate_ncs, validate_scw, validate_srp  # noqa: E402
from simulation_chamber import run_chamber, solid_png  # noqa: E402

FIXTURES = ROOT / "fixtures"
DEFAULT_CHAPTER = FIXTURES / "archive-consent-ch1-excerpt.md"


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def split_beats(markdown: str, *, max_shots: int = 8) -> list[str]:
    """Split chapter into shot actions — heuristic, not Story Forge Movie Lane."""
    # Prefer ## headings, else paragraphs
    parts = re.split(r"\n(?=##\s+)", markdown.strip())
    beats: list[str] = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if part.startswith("#"):
            # strip heading line
            lines = part.splitlines()
            body = "\n".join(lines[1:]).strip() if len(lines) > 1 else lines[0]
            title = re.sub(r"^#+\s*", "", lines[0]).strip()
            action = (title + (": " + body[:160] if body else "")).strip(": ")
        else:
            action = " ".join(part.split())[:200]
        if action:
            beats.append(action)
    if len(beats) < 2:
        paras = [p.strip() for p in re.split(r"\n\s*\n", markdown) if p.strip()]
        beats = [" ".join(p.split())[:200] for p in paras[:max_shots]]
    return beats[:max_shots] or ["Opening beat (empty chapter)"]


def markdown_to_build_artifact(
    markdown: str,
    *,
    production_id: str,
    character_id: str,
    identity_lock: dict[str, Any],
    score_identity: str,
    scene_id: str = "archive-ch1-short",
    setting: str = "Archive of Consent — Chapter 1 (bounded short)",
) -> dict[str, Any]:
    beats = split_beats(markdown)
    shots = []
    for i, action in enumerate(beats):
        shot_id = f"S{i+1:02d}"
        move = "static-establishing" if i == 0 else ("push-in" if i % 2 else "orbit-slow")
        shots.append(
            {
                "shotId": shot_id,
                "shot_number": i + 1,
                "description": action,
                "action": action[:120],
                "framing": "50mm" if i % 2 else "35mm-wide",
                "pose": f"pose-{i+1}",
                "camera_motion": move,
                "duration_seconds": 2.0,
            }
        )
    cues = []
    for i, s in enumerate(shots):
        intensity = round(0.35 + 0.5 * (i / max(1, len(shots) - 1)), 3)
        cues.append(
            {
                "shotId": s["shotId"],
                "audioCueId": f"cue-{s['shotId'].lower()}",
                "cue": "theme-enter" if i == 0 else "theme-develop",
                "intensity": intensity,
                "playback": "loop" if i == 0 else "one-shot",
                "cueStartSeconds": float(i * 2),
                "durationSeconds": 2.0,
                "layers": ["theme"],
            }
        )
    return {
        "build_id": production_id,
        "session_id": f"book-drop-{_digest(production_id)}",
        "scene_id": scene_id,
        "narrative_state": {
            "prompt": setting,
            "setting": setting,
            "tone": "sovereign-mythic",
            "characters": [
                {
                    "characterId": character_id,
                    "name": character_id,
                    "identityLock": identity_lock,
                }
            ],
        },
        "worldPack": {
            "id": f"world-{scene_id}",
            "setting": setting,
            "weather": "overcast",
            "lighting": "archive-amber",
        },
        "temporal_shot_list": {"scene_id": scene_id, "shots": shots},
        "continuityConstraints": {
            "sameCharacterAcrossShots": True,
            "persistentEquipment": True,
            "persistentWorld": True,
        },
        "audioPlan": {
            "statusTag": "declared",
            "mappingStatusTag": "partial",
            "scoreIdentity": score_identity,
            "stems": [
                {
                    "id": "theme-bed",
                    "role": "theme",
                    "playback": "loop",
                    "carriesScoreIdentity": True,
                }
            ],
            "cues": cues,
            "forbiddenDucking": [
                {"stemId": "theme-bed", "reason": "carries scoreIdentity"},
            ],
        },
        "renderIntent": {"summary": "book-drop-nce", "route": "rt4d", "quality": "draft"},
        "provenance": {
            "source": "mandala-book-drop-heuristic",
            "statusTag": "partial_with_gaps",
            "limitation": (
                "Shot list derived by Mandala markdown heuristic — not Infinity Movie Lane. "
                "Replace with Story Forge BackendBuildArtifact for canonical truth."
            ),
            "infinityRepo": "warheart1984-ctrl/infinity",
        },
    }


def run_book_drop(
    *,
    chapter_path: Path,
    out_dir: Path,
    character_id: str,
    identity_lock: dict[str, Any],
    score_identity: str,
    production_id: str | None = None,
    dry_run: bool = True,
    frames_per_shot: int = 3,
    fps: float = 6.0,
    build_json: Path | None = None,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = out_dir / f"book-drop-{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    if build_json and build_json.is_file():
        raw = json.loads(build_json.read_text(encoding="utf-8"))
        source = "infinity_or_operator_build_json"
    else:
        md = chapter_path.read_text(encoding="utf-8")
        pid = production_id or f"sf-build-archive-ch1-{stamp}"
        raw = markdown_to_build_artifact(
            md,
            production_id=pid,
            character_id=character_id,
            identity_lock=identity_lock,
            score_identity=score_identity,
        )
        source = "mandala_markdown_heuristic"
        (run_dir / "build.heuristic.json").write_text(
            json.dumps(raw, indent=2) + "\n", encoding="utf-8"
        )

    mapped = map_build_to_mandala(raw)
    if not mapped["identityEqual"] or not mapped["scoreIdentityEqual"]:
        raise SystemExit(f"identity/score lock failed: {mapped}")

    request = mapped["request"]
    actor = request["actors"][0]
    keyframe = run_dir / "book-keyframe.png"
    keyframe.write_bytes(solid_png(256, 256, (60, 52, 44)))
    srp = stub_srp(keyframe)
    validate_srp(srp)

    painted = paint_keyframe(
        keyframe,
        run_dir / "01-painted.png",
        prompt="cinematic still, archive mythic tone, same identity, emotion layer only",
        dry_run=dry_run,
    )

    frames_all: list[Path] = []
    for shot in request["shotTimeline"]:
        shot_id = shot["shotId"]
        move = str((shot.get("camera") or {}).get("move") or "")
        path_id = "push-in" if "push" in move else ("close-up" if "close" in move else "orbit")
        scw, frames = run_chamber(
            out_dir=run_dir / "shots" / shot_id,
            base_still=Path(painted["uri"]),
            production_id=request["productionId"],
            scene_id=f"book:{shot_id}",
            shot_spec={
                "cameraPathId": path_id,
                "mood": "archive",
                "weatherTags": [],
                "frameCount": frames_per_shot,
            },
            character_id=actor["characterId"],
            identity_lock=actor["identityLock"],
        )
        validate_scw(scw)
        frames_all.extend(Path(fr["uri"]) for fr in frames)

    mp4 = assemble_flipbook_mp4(frames_all, run_dir / "press-play.mp4", fps=fps, with_click=True)
    still_refs = [
        {
            "role": "base_keyframe",
            "uri": str(keyframe),
            "sha256": file_sha256(keyframe),
            "notes": "book-drop keyframe stand-in",
        },
        {
            "role": "copy_fallback" if painted["beautyStatus"] != "beauty_applied_sd_turbo" else "beauty",
            "uri": painted["uri"],
            "sha256": painted["sha256"],
            "notes": painted["beautyStatus"],
        },
        *[
            {
                "role": "sim_frame",
                "uri": str(p),
                "sha256": file_sha256(p),
                "notes": "chamber frame",
            }
            for p in frames_all
        ],
    ]
    ncs = {
        "schemaVersion": SCHEMA_VERSION,
        "kind": "NeuralCinematicSequence",
        "status": "partial_with_gaps",
        "capabilityId": CAPABILITY_ID,
        "sequenceId": f"ncs-book-{stamp}",
        "productionId": request["productionId"],
        "sceneId": "archive-ch1-short",
        "stillRefs": still_refs,
        "modelIds": list(painted.get("modelIds") or []) + ["simulation_chamber.camera_orbit_flipbook"],
        "beautyStatus": painted["beautyStatus"],
        "gaps": [
            "book_shots_from_markdown_heuristic_not_infinity_movie_lane"
            if source == "mandala_markdown_heuristic"
            else "operator_supplied_build_json",
            "fixture_or_stand_in_visuals",
            "click_bed_not_beatbox",
            "movie_lane_assemble_declared",
        ],
        "provenance": {
            "intentId": f"intent-book-{stamp}",
            "worldId": "archive-ch1",
            "timelineId": "timeline-archive-ch1-short",
            "capabilityId": CAPABILITY_ID,
            "artifactHashes": {
                "keyframe": file_sha256(keyframe),
                **{f"f{i:03d}": file_sha256(p) for i, p in enumerate(frames_all)},
            },
            "limitation": "Book drop short — partial_with_gaps; replace heuristic with Infinity emit.",
        },
        "pressPlayMp4": mp4.get("path") if mp4.get("ok") else None,
        "organs": {
            "storyForge": source,
            "simulationChamber": "partial_with_gaps",
            "movieLane": "declared",
        },
        "limitation": "Bounded Chapter 1 short flipbook — not the whole novel, not photoreal.",
    }
    validate_ncs(ncs)
    ncs_path = run_dir / "ncs.json"
    ncs_path.write_text(json.dumps(ncs, indent=2) + "\n", encoding="utf-8")
    summary = {
        "status": "partial_with_gaps",
        "source": source,
        "runDir": str(run_dir),
        "ncsPath": str(ncs_path),
        "pressPlayMp4": mp4,
        "characterId": actor["characterId"],
        "productionId": request["productionId"],
        "shotCount": mapped["shotCount"],
        "identityEqual": mapped["identityEqual"],
        "gaps": ncs["gaps"],
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Book drop → NCE press-Play short")
    p.add_argument("--chapter", default=str(DEFAULT_CHAPTER))
    p.add_argument("--build-json", default="", help="Infinity/operator BackendBuildArtifact JSON")
    p.add_argument("--out-dir", default=str(ROOT / "outputs"))
    p.add_argument("--character-id", default="archive-witness-01")
    p.add_argument("--score-identity", default="archive-consent-ch1-theme-v1")
    p.add_argument("--species", default="human")
    p.add_argument("--face-ref", default="face-archive-witness")
    p.add_argument("--body-build", default="lean")
    p.add_argument("--armor-id", default="none")
    p.add_argument("--weapon-id", default="none")
    p.add_argument("--frames-per-shot", type=int, default=3)
    p.add_argument("--fps", type=float, default=6.0)
    p.add_argument("--live-paint", action="store_true")
    args = p.parse_args(argv)

    lock = {
        "species": args.species,
        "rigSpecies": args.species,
        "faceRefId": args.face_ref,
        "bodyBuild": args.body_build,
        "armorId": args.armor_id,
        "weaponId": args.weapon_id,
        "weaponHeldIn": "none",
        "meshHash": "sha256:archive-ch1-witness-mesh-declared",
        "rigHash": "sha256:archive-ch1-witness-rig-declared",
        "prohibitedMutations": ["identity-drift", "species-swap"],
    }
    summary = run_book_drop(
        chapter_path=Path(args.chapter),
        out_dir=Path(args.out_dir),
        character_id=args.character_id,
        identity_lock=lock,
        score_identity=args.score_identity,
        dry_run=not args.live_paint,
        frames_per_shot=args.frames_per_shot,
        fps=args.fps,
        build_json=Path(args.build_json) if args.build_json else None,
    )
    print("============================================================")
    print(" Book drop → Simulation Chamber press-Play")
    print("============================================================")
    print("source=", summary["source"])
    print("runDir=", summary["runDir"])
    print("characterId=", summary["characterId"])
    print("shots=", summary["shotCount"])
    print("identityEqual=", summary["identityEqual"])
    if summary["pressPlayMp4"].get("ok"):
        print("pressPlayMp4=", summary["pressPlayMp4"]["path"])
    else:
        print("mp4 failed:", summary["pressPlayMp4"])
        return 1
    print("status=", summary["status"])
    print("NOTE: heuristic shots ≠ Infinity Movie Lane until --build-json from Story Forge.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
