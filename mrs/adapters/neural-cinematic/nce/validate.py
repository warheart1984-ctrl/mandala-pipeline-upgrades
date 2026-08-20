"""Structural validators for neural-cinematic/0.1 artifacts.

Status: **partial** — schema-shaped checks; no GPU.
Does not invent narrative identity from filenames.
Requires explicit `gaps: []` on SCW / NCS / SRP where applicable.
"""

from __future__ import annotations

from typing import Any

from . import CAPABILITY_ID, IDENTITY_LOCK_KEYS, SCHEMA_VERSION

CAMERA_PATHS = frozenset({"push-in", "orbit", "close-up"})
BEAUTY_STATUSES = frozenset(
    {
        "beauty_applied_sd_turbo",
        "beauty_skipped_bridge_down",
        "beauty_skipped_disabled",
        "beauty_skipped_dry_run",
    }
)
STATUS_TAGS = frozenset({"declared", "declared_stub", "partial", "partial_with_gaps"})


class NceContractError(ValueError):
    """Artifact failed the NCE contract."""


def _req_dict(data: Any, name: str) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise NceContractError(f"{name} must be an object")
    return data


def _req_str(obj: dict[str, Any], key: str) -> str:
    val = obj.get(key)
    if not isinstance(val, str) or not val.strip():
        raise NceContractError(f"missing or empty string: {key}")
    return val


def _req_gaps(obj: dict[str, Any], *, allow_empty: bool = False) -> list[Any]:
    gaps = obj.get("gaps")
    if not isinstance(gaps, list):
        raise NceContractError("gaps must be an array")
    if not allow_empty and len(gaps) < 1:
        raise NceContractError("gaps must list at least one known limitation")
    for i, g in enumerate(gaps):
        if not isinstance(g, str) or not g.strip():
            raise NceContractError(f"gaps[{i}] must be a non-empty string")
    return gaps


def _version(obj: dict[str, Any]) -> None:
    if obj.get("schemaVersion") != SCHEMA_VERSION:
        raise NceContractError(f"schemaVersion must be {SCHEMA_VERSION!r}")


def _capability(obj: dict[str, Any]) -> None:
    if obj.get("capabilityId") != CAPABILITY_ID:
        raise NceContractError(f"capabilityId must be {CAPABILITY_ID!r}")


def _shot_spec(spec: Any) -> dict[str, Any]:
    s = _req_dict(spec, "shotSpec")
    path_id = _req_str(s, "cameraPathId")
    if path_id not in CAMERA_PATHS:
        raise NceContractError(f"shotSpec.cameraPathId must be one of {sorted(CAMERA_PATHS)}")
    if "frameCount" in s and s["frameCount"] is not None:
        fc = s["frameCount"]
        if not isinstance(fc, int) or fc < 1 or fc > 64:
            raise NceContractError("shotSpec.frameCount must be int 1..64")
    return s


def _optional_identity(obj: dict[str, Any]) -> None:
    """Refuse filename-shaped invention: characterId may be null; if set must be non-empty str."""
    cid = obj.get("characterId")
    if cid is not None and (not isinstance(cid, str) or not cid.strip()):
        raise NceContractError("characterId must be null or a non-empty string (never invent from filename)")
    lock = obj.get("identityLock")
    if lock is None:
        return
    if not isinstance(lock, dict):
        raise NceContractError("identityLock must be an object or null")
    for key in lock:
        if key not in IDENTITY_LOCK_KEYS:
            raise NceContractError(f"identityLock unknown key {key!r} (storyforge-boundary compatible subset only)")


def validate_srp(data: Any) -> dict[str, Any]:
    obj = _req_dict(data, "SceneReconstructionPackage")
    _version(obj)
    _capability(obj)
    if obj.get("kind") != "SceneReconstructionPackage":
        raise NceContractError("kind must be SceneReconstructionPackage")
    if obj.get("status") != "declared_stub":
        raise NceContractError("SRP status must be declared_stub (photo→3D not implemented)")
    _req_str(obj, "sourceImageRef")
    _req_gaps(obj)
    return obj


def validate_scw(data: Any) -> dict[str, Any]:
    obj = _req_dict(data, "SimulatedCinematicWorld")
    _version(obj)
    _capability(obj)
    if obj.get("kind") != "SimulatedCinematicWorld":
        raise NceContractError("kind must be SimulatedCinematicWorld")
    status = obj.get("status")
    if status not in ("declared", "partial", "partial_with_gaps"):
        raise NceContractError("SCW status must be declared, partial, or partial_with_gaps")
    _req_str(obj, "sceneId")
    _req_str(obj, "productionId")
    _shot_spec(obj.get("shotSpec"))
    _optional_identity(obj)
    if obj.get("cosmosRequired") not in (None, False):
        raise NceContractError("cosmosRequired must be false or omitted (Simulation Chamber skip-Cosmos path)")
    _req_gaps(obj)
    return obj


def validate_ncs(data: Any) -> dict[str, Any]:
    obj = _req_dict(data, "NeuralCinematicSequence")
    _version(obj)
    _capability(obj)
    if obj.get("kind") != "NeuralCinematicSequence":
        raise NceContractError("kind must be NeuralCinematicSequence")
    if obj.get("status") not in ("partial", "partial_with_gaps", "declared"):
        raise NceContractError("NCS status must be partial, partial_with_gaps, or declared")
    _req_str(obj, "sequenceId")
    stills = obj.get("stillRefs")
    if not isinstance(stills, list) or len(stills) < 1:
        raise NceContractError("stillRefs must be a non-empty array")
    for i, ref in enumerate(stills):
        r = _req_dict(ref, f"stillRefs[{i}]")
        _req_str(r, "role")
        _req_str(r, "uri")
        sha = _req_str(r, "sha256")
        if len(sha) != 64 or any(c not in "0123456789abcdef" for c in sha):
            raise NceContractError(f"stillRefs[{i}].sha256 must be 64 lowercase hex")
    models = obj.get("modelIds")
    if not isinstance(models, list):
        raise NceContractError("modelIds must be an array")
    prov = _req_dict(obj.get("provenance"), "provenance")
    for key in ("intentId", "worldId", "timelineId"):
        _req_str(prov, key)
    if prov.get("capabilityId") != CAPABILITY_ID:
        raise NceContractError(f"provenance.capabilityId must be {CAPABILITY_ID!r}")
    hashes = prov.get("artifactHashes")
    if not isinstance(hashes, dict) or not hashes:
        raise NceContractError("provenance.artifactHashes must be a non-empty object")
    for hk, hv in hashes.items():
        if not isinstance(hv, str) or len(hv) != 64 or any(c not in "0123456789abcdef" for c in hv):
            raise NceContractError(f"provenance.artifactHashes[{hk}] must be 64 lowercase hex")
    mid = prov.get("modelIds")
    if mid is not None and not isinstance(mid, list):
        raise NceContractError("provenance.modelIds must be an array when present")
    beauty = obj.get("beautyStatus")
    if beauty is not None and beauty not in BEAUTY_STATUSES:
        raise NceContractError(f"beautyStatus invalid: {beauty!r}")
    _req_gaps(obj)
    return obj


def validate_request(data: Any) -> dict[str, Any]:
    obj = _req_dict(data, "NeuralCinematicRequest")
    _version(obj)
    _capability(obj)
    if obj.get("kind") != "NeuralCinematicRequest":
        raise NceContractError("kind must be NeuralCinematicRequest")
    _req_str(obj, "style")
    intens = obj.get("emotion_intensity")
    if not isinstance(intens, (int, float)) or intens < 0 or intens > 1:
        raise NceContractError("emotion_intensity must be number 0..1")
    if not isinstance(obj.get("requires_simulation"), bool):
        raise NceContractError("requires_simulation must be boolean")
    _shot_spec(obj.get("shotSpec"))
    _optional_identity(obj)
    if obj.get("characterId") is None and obj.get("baseKeyframePath"):
        pass
    return obj
