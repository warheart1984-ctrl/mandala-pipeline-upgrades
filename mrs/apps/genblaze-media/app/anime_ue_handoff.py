"""Thin Genblaze → UE AnimeStylizer handoff (partial).

POST /api/anime returns a structure/cel plate handoff package with provenance
pointing at AnimeWorldProfile + projection_method. Does **not** claim a full
UE compile, RDG stylize, or ffmpeg CI artifact.

Drive-G-1:
  - Status: **partial** (handoff + provenance declared; live Engine3D optional)
  - Print SoT / Digital Printer untouched
  - UE AnimeStylizer remains skeleton/partial (optional consumer leg)
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.anime_world_profile import (
    default_example_path,
    load_anime_world_profile,
    validate_anime_world_profile,
)

ANIME_UE_ENDPOINT = "/api/anime"
ANIME_UE_KIND = "anime-ue-handoff"
STATUS = "partial"
CONTRACT_REL = (
    "docs/4d-engine/projection/ANIME_STRUCTURE_PLATE_PROJECTOR_CONTRACT.v1.md"
)
PROVENANCE_SCHEMA_REL = (
    "schemas/4d-engine/v1/StructurePlateProjectionProvenance.v1.schema.json"
)
UE_PLUGIN_REL = "unreal/AnimeStylizer"

_REFERENCE_MODELS = {
    "projector4d-sot": {
        "projector_id": "projector4d-sot",
        "projection_method": "projector4d-sot",
        "reference_model": "Projector4D (d4/(d4+w)) · Print SoT closed form (structure-lane candidate)",
        "alpha": None,
        "d4": 1.0,
    },
    "drop_w": {
        "projector_id": "drop_w",
        "projection_method": "drop_w",
        "reference_model": "drop_w — literal XYZ (fourth axis discarded)",
        "alpha": None,
        "d4": None,
    },
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def normalize_projection_method(method: str | None) -> str:
    key = (method or "projector4d-sot").strip().lower().replace("_", "-")
    if key in ("projector4d", "projector4d-sot", "projector-4d", "sot"):
        return "projector4d-sot"
    if key in ("drop-w", "dropw", "literal-xyz"):
        return "drop_w"
    return "projector4d-sot"


def build_structure_plate_provenance(
    *,
    projection_method: str,
    anime_world_profile_id: str,
    asset_sha256: str | None = None,
) -> dict[str, Any]:
    """Provenance block aligned with StructurePlateProjectionProvenance.v1 (declared)."""
    method = normalize_projection_method(projection_method)
    ref = _REFERENCE_MODELS[method]
    prov: dict[str, Any] = {
        "schema": PROVENANCE_SCHEMA_REL,
        "projector_id": ref["projector_id"],
        "projection_method": ref["projection_method"],
        "reference_model": ref["reference_model"],
        "lane": "anime-structure",
        "print_sot_touched": False,
        "digital_printer_touched": False,
        "anime_world_profile_id": anime_world_profile_id,
        "contract": CONTRACT_REL,
        "status": "declared",
    }
    if ref["d4"] is not None:
        prov["d4"] = ref["d4"]
        if ref["d4"]:
            prov["alpha"] = 1.0 / float(ref["d4"])
    if method == "drop_w":
        prov["alpha"] = None
        prov["d4"] = None
    if asset_sha256:
        prov["asset_sha256"] = asset_sha256
    return prov


def anime_ue_availability() -> dict[str, Any]:
    profile_path = default_example_path()
    profile_id = None
    profile_valid = False
    if profile_path.is_file():
        try:
            profile = load_anime_world_profile(profile_path)
            issues = validate_anime_world_profile(profile)
            profile_id = profile.get("profileId")
            profile_valid = len(issues) == 0
        except (OSError, ValueError) as exc:
            profile_valid = False
            return {
                "endpoint": ANIME_UE_ENDPOINT,
                "kind": ANIME_UE_KIND,
                "status": STATUS,
                "available": True,
                "example_profile_id": None,
                "example_profile_valid": False,
                "example_error": str(exc),
                "ue_plugin": UE_PLUGIN_REL,
                "ue_status": "skeleton/partial",
                "note": (
                    "POST /api/anime returns structure/cel handoff + provenance. "
                    "UE AnimeStylizer is optional; reliable demo is Genblaze→structure→ffmpeg."
                ),
            }
    return {
        "endpoint": ANIME_UE_ENDPOINT,
        "kind": ANIME_UE_KIND,
        "status": STATUS,
        "available": True,
        "example_profile_id": profile_id,
        "example_profile_valid": profile_valid,
        "ue_plugin": UE_PLUGIN_REL,
        "ue_status": "skeleton/partial",
        "contract": CONTRACT_REL,
        "note": (
            "POST /api/anime returns structure/cel handoff + provenance. "
            "UE AnimeStylizer is optional; reliable demo is Genblaze→structure→ffmpeg."
        ),
    }


def build_anime_ue_handoff(
    *,
    projection_method: str = "projector4d-sot",
    anime_world_profile_path: str | Path | None = None,
    prompt: str | None = None,
    dry_run: bool = True,
    structure_png: bytes | None = None,
    structure_preview_url: str | None = None,
    structure_run_id: str | None = None,
    width: int = 256,
    height: int = 256,
) -> dict[str, Any]:
    """Assemble UE handoff JSON (partial). Live plate optional via structure_png."""
    path = Path(anime_world_profile_path) if anime_world_profile_path else default_example_path()
    profile = load_anime_world_profile(path)
    issues = validate_anime_world_profile(profile)
    if issues:
        raise ValueError(f"AnimeWorldProfile invalid: {', '.join(issues)}")

    profile_id = str(profile.get("profileId") or "unknown")
    method = normalize_projection_method(projection_method)
    run_id = structure_run_id or str(uuid.uuid4())
    asset_sha: str | None = None
    if structure_png is not None:
        asset_sha = hashlib.sha256(structure_png).hexdigest()

    provenance = build_structure_plate_provenance(
        projection_method=method,
        anime_world_profile_id=profile_id,
        asset_sha256=asset_sha,
    )

    structure: dict[str, Any] | None = None
    if structure_png is not None or structure_preview_url:
        structure = {
            "run_id": run_id,
            "kind": "anime-structure-plate",
            "width": width,
            "height": height,
            "asset_sha256": asset_sha,
            "preview_url": structure_preview_url,
            "bytes_present": structure_png is not None,
            "source": "live" if structure_png is not None and not dry_run else "handoff",
        }

    return {
        "status": STATUS,
        "kind": ANIME_UE_KIND,
        "run_id": run_id,
        "created_at": _utc_now(),
        "dry_run": dry_run,
        "prompt": (prompt or "").strip() or None,
        "anime_world_profile_id": profile_id,
        "anime_world_profile_version": profile.get("schemaVersion"),
        "anime_world_profile_path": str(path).replace("\\", "/"),
        "anime_world_profile_status": profile.get("status"),
        "projection_method": method,
        "provenance": provenance,
        "structure": structure,
        "capability_tags": {
            "genblaze_api_anime": "partial",
            "structure_plate": "partial" if structure else "declared",
            "ue_anime_stylizer": "skeleton/partial",
            "ffmpeg_export": "declared",
            "replay": "declared",
            "print_sot": "untouched",
        },
        "ue_consumer": {
            "plugin_path": UE_PLUGIN_REL,
            "plugin_status": "skeleton/partial",
            "load_api": "UAnimeStylizerBlueprintLibrary::LoadStructurePlate",
            "config_api": "FAnimeStylizerConfig (bUseStructurePlate, StructureBlend)",
            "contract": CONTRACT_REL,
            "note": (
                "Optional leg. Reliable hackathon demo does not require UE compile — "
                "use Genblaze structure plate → ffmpeg."
            ),
        },
        "pipeline_story": [
            "intent",
            "genblaze:/api/anime",
            "structure_plate+provenance",
            "ue:AnimeStylizer (optional)",
            "ffmpeg",
            "evidence",
            "replay (declared)",
        ],
        "non_claims": [
            "Not Full Photoreal / Digital Printer SoT",
            "Not a verified UE 5.3+ compile in this repo",
            "Not CKL-enforced provenance (declared schema only)",
            "Not a measured R9 380 / 1.1 ms profile",
            "ffmpeg H.264 cleanliness is operator-side (declared unless artifact hashed)",
        ],
        "note": (
            "Governed creative pipeline handoff. Structure/cel plate + AnimeWorldProfile "
            "+ projection_method provenance for UE or ffmpeg consumers."
        ),
    }
