"""Phase 5 quality probes — declared / partial_with_gaps only.

Does not implement production sculpt or Cosmos. Reports whether related paths exist.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MRS = ROOT.parents[1]
REPO = ROOT.parents[2]


def probe() -> dict:
    sculptor = MRS / "packages" / "sovereign-sculptor"
    if not sculptor.is_dir():
        sculptor = Path("/media/jon/New Volume/Mandala Rendering Software/mrs/packages/sovereign-sculptor")
    daniel = REPO / "daniel_blueprint"
    # worktree may not have daniel; check Mandala volume
    mandala = Path("/media/jon/New Volume/Mandala Rendering Software")
    if not daniel.exists():
        daniel = mandala / "daniel_blueprint"
    preview_wt = Path("/media/jon/New Volume/mrs-feat-rt4d-preview-contracts")
    return {
        "status": "declared",
        "gaps": [
            "production_sculpt_not_wired_into_nce",
            "engine3d_soft_raster_not_default_chamber_backend",
            "cosmos_optional_not_required",
        ],
        "sovereignSculptor": {
            "path": str(sculptor),
            "present": sculptor.is_dir(),
            "status": "partial" if sculptor.is_dir() else "declared",
        },
        "danielBlueprint": {
            "path": str(daniel),
            "present": daniel.is_dir(),
            "status": "partial" if daniel.is_dir() else "declared",
        },
        "previewContractsWorktree": {
            "path": str(preview_wt),
            "present": preview_wt.is_dir(),
            "status": "partial" if preview_wt.is_dir() else "declared",
        },
        "cosmos": {
            "status": "declared_optional",
            "cosmosRequired": False,
            "note": "Simulation Chamber is the local skip-Cosmos motion organ",
        },
        "next": [
            "Replace fixture clay with Sovereign Sculptor production mesh under identityLock",
            "Hash-verify GLB before GLTFLoader (preview contracts)",
            "Optional: Daniel Cycles on NVIDIA host; never block RX 580 demo",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(probe(), indent=2))
