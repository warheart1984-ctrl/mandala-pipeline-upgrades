"""Conformance Evidence: Genblaze / Engine3D tile ROI API inventory (Cycle 7)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
GENBLAZE_APP = REPO / "apps" / "genblaze-media" / "app"
ENGINE3D_PROVIDER = GENBLAZE_APP / "engine3d_still_provider.py"
GENBLAZE_MAIN = GENBLAZE_APP / "main.py"

TILE_API_PATTERNS = (
    r"\bcrop_region\b",
    r"\btile_index\b",
    r"\bregion_x\b",
    r"\bviewport_crop\b",
    r"per[-_]tile",
    r"/api/.*tile",
)


def _scan_for_tile_api(path: Path) -> list[str]:
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    hits: list[str] = []
    for pat in TILE_API_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            hits.append(pat)
    return hits


class TestGenblazeTileApiInventory:
    """Drive-G-1: document absence of per-tile shade API — W-TILE-FAITHFUL stays blocked."""

    def test_engine3d_still_has_no_tile_crop_parameters(self):
        hits = _scan_for_tile_api(ENGINE3D_PROVIDER)
        assert hits == [], f"unexpected tile API signals in engine3d_still_provider: {hits}"

    def test_genblaze_main_has_no_tile_render_route(self):
        hits = _scan_for_tile_api(GENBLAZE_MAIN)
        # Allow HTML viewport meta only — exclude if only in static paths
        filtered = [h for h in hits if h not in {r"per[-_]tile", r"/api/.*tile"}]
        assert filtered == [], f"unexpected tile API in genblaze main: {filtered}"

    @pytest.mark.xfail(
        strict=True,
        reason="W-TILE-FAITHFUL blocked-on-downstream-API — certification requires Genblaze tile still API",
    )
    def test_tile_faithful_conformance_cleared(self):
        pytest.fail(
            "Per-tile Genblaze shading not available; minimum change: "
            "engine3d-still accepts crop_region {x,y,w,h} or dedicated /api/engine3d-tile-still",
        )
