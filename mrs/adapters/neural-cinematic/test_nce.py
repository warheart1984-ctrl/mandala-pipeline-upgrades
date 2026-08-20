"""Contract + dry-run tests for neural-cinematic adapter (no GPU)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aais import WORKER_IDS, worker_stub_manifest
from mythar import MytharBoundaryError, accept_audio_plan
from nce import CAPABILITY_ID, SCHEMA_VERSION
from nce.validate import (
    NceContractError,
    validate_ncs,
    validate_request,
    validate_scw,
    validate_srp,
)
from simulation_chamber import camera_pose, run_chamber, solid_png

CONTRACTS = ROOT / "contracts"


def _load_schema(name: str) -> dict:
    return json.loads((CONTRACTS / name).read_text(encoding="utf-8"))


def test_capability_and_schema_version_constants():
    assert CAPABILITY_ID == "neural_cinematic_simulation_backend"
    assert SCHEMA_VERSION == "neural-cinematic/0.1"
    for name in (
        "SceneReconstructionPackage.schema.json",
        "SimulatedCinematicWorld.schema.json",
        "NeuralCinematicSequence.schema.json",
        "NeuralCinematicRequest.schema.json",
    ):
        schema = _load_schema(name)
        assert schema["properties"]["schemaVersion"]["const"] == SCHEMA_VERSION
        if "capabilityId" in schema["properties"]:
            assert schema["properties"]["capabilityId"]["const"] == CAPABILITY_ID


def test_srp_must_be_declared_stub():
    ok = {
        "schemaVersion": SCHEMA_VERSION,
        "kind": "SceneReconstructionPackage",
        "status": "declared_stub",
        "capabilityId": CAPABILITY_ID,
        "sourceImageRef": "fixtures/keyframe-64.png",
        "gaps": ["no_monocular_depth"],
    }
    validate_srp(ok)
    bad = {**ok, "status": "partial"}
    with pytest.raises(NceContractError, match="declared_stub"):
        validate_srp(bad)


def test_request_rejects_empty_character_and_unknown_lock_keys():
    base = {
        "schemaVersion": SCHEMA_VERSION,
        "kind": "NeuralCinematicRequest",
        "capabilityId": CAPABILITY_ID,
        "style": "cinematic",
        "emotion_intensity": 0.5,
        "requires_simulation": True,
        "shotSpec": {"cameraPathId": "orbit", "frameCount": 4},
        "characterId": None,
        "baseKeyframePath": "/tmp/warrior.png",
    }
    validate_request(base)
    with pytest.raises(NceContractError, match="characterId"):
        validate_request({**base, "characterId": "   "})
    with pytest.raises(NceContractError, match="unknown key"):
        validate_request({**base, "identityLock": {"madeUpField": "x"}})


def test_scw_cosmos_must_not_be_required():
    scw = {
        "schemaVersion": SCHEMA_VERSION,
        "kind": "SimulatedCinematicWorld",
        "status": "partial_with_gaps",
        "capabilityId": CAPABILITY_ID,
        "sceneId": "s1",
        "productionId": "p1",
        "shotSpec": {"cameraPathId": "push-in", "frameCount": 2},
        "cosmosRequired": False,
        "rendererBackend": "camera_orbit_flipbook",
        "gaps": ["ken_burns_or_orbit_metadata_only_not_true_3d_motion"],
    }
    validate_scw(scw)
    with pytest.raises(NceContractError, match="cosmosRequired"):
        validate_scw({**scw, "cosmosRequired": True})


def test_simulation_chamber_flipbook_dry(tmp_path: Path):
    key = tmp_path / "k.png"
    key.write_bytes(solid_png(64, 64, (10, 20, 30)))
    scw, frames = run_chamber(
        out_dir=tmp_path / "frames",
        base_still=key,
        production_id="p1",
        scene_id="s1",
        shot_spec={"cameraPathId": "orbit", "frameCount": 4, "mood": "calm"},
        character_id=None,
        identity_lock=None,
    )
    validate_scw(scw)
    assert scw["status"] == "partial_with_gaps"
    assert scw["cosmosRequired"] is False
    assert isinstance(scw["gaps"], list) and len(scw["gaps"]) >= 1
    assert len(frames) == 4
    assert frames[0]["sha256"] != frames[-1]["sha256"]
    assert "azimuth_deg" in camera_pose("orbit", 0.5)
    assert frames[0]["buffers"]["depthBuffer"]["status"] == "declared"


def test_ncs_partial_with_honest_beauty_status(tmp_path: Path):
    png = tmp_path / "a.png"
    png.write_bytes(solid_png(64, 64, (1, 2, 3)))
    sha = __import__("nce.canonical", fromlist=["file_sha256"]).file_sha256(png)
    ncs = {
        "schemaVersion": SCHEMA_VERSION,
        "kind": "NeuralCinematicSequence",
        "status": "partial_with_gaps",
        "capabilityId": CAPABILITY_ID,
        "sequenceId": "ncs-test",
        "stillRefs": [{"role": "base_keyframe", "uri": str(png), "sha256": sha}],
        "modelIds": ["simulation_chamber.camera_orbit_flipbook"],
        "beautyStatus": "beauty_skipped_dry_run",
        "gaps": ["not_movie_lane_assemble"],
        "provenance": {
            "intentId": "i",
            "worldId": "w",
            "timelineId": "t",
            "capabilityId": CAPABILITY_ID,
            "artifactHashes": {"keyframe": sha},
        },
    }
    validate_ncs(ncs)


def test_demo_pipeline_dry_run(tmp_path: Path):
    from demo_pipeline import main

    code = main(
        [
            "--dry-run",
            "--out-dir",
            str(tmp_path),
            "--frames",
            "3",
            "--camera-path",
            "close-up",
            "--score-identity",
            "demo-theme-v1",
        ]
    )
    assert code == 0
    runs = list(tmp_path.glob("nce-run-*"))
    assert len(runs) == 1
    ncs = json.loads((runs[0] / "ncs.json").read_text(encoding="utf-8"))
    assert ncs["status"] == "partial_with_gaps"
    assert ncs["beautyStatus"] == "beauty_skipped_dry_run"
    assert ncs["organs"]["cosmos"] == "declared_optional_skipped"
    assert ncs["mytharAudioRef"]["scoreIdentity"] == "demo-theme-v1"
    assert ncs["provenance"]["capabilityId"] == CAPABILITY_ID
    assert ncs["gaps"]
    validate_ncs(ncs)


def test_mythar_and_aais_stubs():
    ref = accept_audio_plan({"scoreIdentity": "theme-a", "cues": [{"shotId": "S01"}]})
    assert ref["status"] == "declared"
    with pytest.raises(MytharBoundaryError):
        accept_audio_plan({"scoreIdentity": "  "})
    man = worker_stub_manifest()
    assert man["status"] == "declared"
    assert man["runtimeHostedInMandala"] is False
    assert "aais.painter_pass" in WORKER_IDS


def test_filename_must_not_become_identity():
    """Operator may pass a path named warrior.png without inventing characterId."""
    req = {
        "schemaVersion": SCHEMA_VERSION,
        "kind": "NeuralCinematicRequest",
        "capabilityId": CAPABILITY_ID,
        "style": "cinematic",
        "emotion_intensity": 0.2,
        "requires_simulation": True,
        "baseKeyframePath": "/tmp/warrior-anthro-fox.png",
        "shotSpec": {"cameraPathId": "orbit"},
        "characterId": None,
    }
    out = validate_request(req)
    assert out["characterId"] is None
    assert "warrior" not in (out.get("characterId") or "")


def test_warrior_short_press_play(tmp_path: Path):
    from demo_short_warrior import run_warrior_short

    summary = run_warrior_short(
        out_dir=tmp_path,
        dry_run=True,
        frames_per_shot=2,
        fps=4.0,
    )
    assert summary["identityCompare"]["equal"] is True
    assert summary["scoreIdentityCompare"]["equal"] is True
    assert summary["characterId"] == "warrior-anthro-fox-01"
    assert summary["pressPlayMp4"]["ok"] is True
    assert Path(summary["pressPlayMp4"]["path"]).is_file()
    assert summary["status"] == "partial_with_gaps"
    ncs = json.loads(Path(summary["ncsPath"]).read_text(encoding="utf-8"))
    validate_ncs(ncs)
