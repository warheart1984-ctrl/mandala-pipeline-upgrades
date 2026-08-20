"""Infinity / Story Forge root discovery + Mandala handoff helpers.

Does not rebuild Story Forge. Locates `warheart1984-ctrl/infinity` on disk and
validates that Mandala's storyforge-boundary map accepts BackendBuildArtifact-shaped JSON.

Status: **partial** for fixture parity; live Movie Lane invoke remains **declared** until
operators run Infinity organs with their own deps.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

INFINITY_CANDIDATES = (
    Path(os.environ.get("INFINITY_ROOT", "")),
    Path("/media/jon/New Volume/Project Infinity"),
    Path("/media/jon/New Volume/infinity"),
    Path.home() / "infinity",
)

BOUNDARY = Path(__file__).resolve().parent.parent / "storyforge-boundary"
WARRIOR_FIXTURE = (
    BOUNDARY / "contract" / "fixtures" / "infinity-backend-build-warrior-courtyard.json"
)


def find_infinity_root() -> Path | None:
    for root in INFINITY_CANDIDATES:
        if not root or str(root) == ".":
            continue
        if (root / "external" / "story_forge").is_dir() or (root / "src" / "story_forge_lane_organ.py").is_file():
            return root.resolve()
    return None


def story_forge_src(root: Path | None = None) -> Path | None:
    root = root or find_infinity_root()
    if not root:
        return None
    src = root / "external" / "story_forge" / "src"
    return src if src.is_dir() else None


def beatbox_lane_path(root: Path | None = None) -> Path | None:
    root = root or find_infinity_root()
    if not root:
        return None
    p = root / "external" / "beatbox_speakers" / "src" / "beatbox" / "lanes" / "beatbox_lane.py"
    return p if p.is_file() else None


def load_warrior_fixture() -> dict[str, Any]:
    return json.loads(WARRIOR_FIXTURE.read_text(encoding="utf-8"))


def map_build_to_mandala(raw: dict[str, Any]) -> dict[str, Any]:
    if str(BOUNDARY) not in sys.path:
        sys.path.insert(0, str(BOUNDARY))
    from contract.map_infinity import from_infinity_backend_build, to_mandala_production_request
    from contract.vertical_slice import compare_identity, emit_shot_artifacts
    from contract.audio import compare_score_identity

    artifact = from_infinity_backend_build(raw)
    request = to_mandala_production_request(artifact)
    shots = emit_shot_artifacts(request)
    return {
        "status": "partial",
        "infinityRoot": str(find_infinity_root()) if find_infinity_root() else None,
        "productionId": request["productionId"],
        "characterId": request["actors"][0]["characterId"],
        "shotCount": len(shots),
        "identityEqual": compare_identity(shots[0], shots[-1])["equal"],
        "scoreIdentityEqual": compare_score_identity(shots[0], shots[-1])["equal"],
        "artifact": artifact,
        "request": request,
        "gaps": [
            "live_movie_lane_invoke_declared",
            "fixture_or_exported_json_not_in_process_story_bible",
        ],
    }


def try_import_backend_build_artifact() -> dict[str, Any]:
    """Attempt import of Infinity BackendBuildArtifact (declared if deps missing)."""
    src = story_forge_src()
    if not src:
        return {
            "ok": False,
            "status": "declared",
            "gaps": ["infinity_root_missing"],
            "why": "INFINITY_ROOT / Project Infinity not found",
        }
    sys.path.insert(0, str(src))
    try:
        from story_forge.backend_full_build import BackendBuildArtifact  # type: ignore

        return {
            "ok": True,
            "status": "partial",
            "class": BackendBuildArtifact.__name__,
            "module": BackendBuildArtifact.__module__,
            "storyForgeSrc": str(src),
            "gaps": ["movie_lane_full_run_not_executed_in_this_helper"],
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "status": "declared",
            "gaps": ["story_forge_import_failed"],
            "why": str(exc)[:300],
            "storyForgeSrc": str(src),
        }


def parity_report() -> dict[str, Any]:
    """Warrior fixture maps through Mandala; Infinity root present for later live emit."""
    mapped = map_build_to_mandala(load_warrior_fixture())
    inf = find_infinity_root()
    bb = try_import_backend_build_artifact()
    return {
        "status": "partial_with_gaps" if inf and mapped["identityEqual"] else "declared",
        "infinityRoot": str(inf) if inf else None,
        "storyForgeExternal": str(story_forge_src()) if story_forge_src() else None,
        "beatboxLane": str(beatbox_lane_path()) if beatbox_lane_path() else None,
        "warriorFixtureParity": {
            "productionId": mapped["productionId"],
            "characterId": mapped["characterId"],
            "identityEqual": mapped["identityEqual"],
            "scoreIdentityEqual": mapped["scoreIdentityEqual"],
            "shotCount": mapped["shotCount"],
        },
        "backendBuildArtifactImport": bb,
        "gaps": [
            "generated_infinity_artifact_export_not_yet_replacing_hand_fixture",
            "operators_must_run_story_forge_movie_lane_to_emit_live_json",
        ]
        + list(mapped.get("gaps") or []),
    }


if __name__ == "__main__":
    print(json.dumps(parity_report(), indent=2))
