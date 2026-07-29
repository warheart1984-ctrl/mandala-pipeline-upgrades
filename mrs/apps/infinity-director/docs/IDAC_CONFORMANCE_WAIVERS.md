# IDAC Conformance Waivers (frozen Core v0.1)

**Status:** **enforced** (process) — waivers are explicit; they do **not** upgrade evidence class.

| Waiver ID | Feature | Evidence blocked | Reason | Revisit |
|-----------|---------|------------------|--------|---------|
| `W-TILE-FAITHFUL` | Per-tile Genblaze shading | Conformance (tile replay), Performance (tile speedup) | **blocked-on-downstream-API** — Genblaze Engine3D still is full-frame only (Cycle 7 inventory) | Genblaze `crop_region` or `/api/engine3d-tile-still` + tests |
| `W-CKL-CHARTER-MRS` | MRS engine CKL loads IDAC charter | Conformance (platform constitutional gate) | MRS `GovernanceKernel` / CKL SoT out of Director scope | MRS CKL integration trail |
| `W-BIT-IDENTICAL` | Bit-identical replay | Conformance (replay) | No tile timing stream from Genblaze | Replay service + timings |
| `W-L2-MULTI` | ai/compile domains in one session | Conformance L2 | Declared stubs only | Domain implementation |
| `W-WORK-UNIT-SPEEDUP` | ATCM estimated_speedup as Performance | Performance | `estimate_not_measured` work model | Replace with harness wall-clock only |

## W-CKL-CHARTER — Cycle 7 (IDAC-local **cleared**)

**Decision:** **IDAC-local charter gate** loads `docs/IDAC_CONSTITUTION.md` + `app/idac/data/idac-invariants.json`, evaluates Intent→Plan→Evidence before dispatch (`app/idac/core/charter_gate.py`). Tests: `test_idac_charter_gate.py`.

**Note:** This does **not** bind MRS engine CKL. Residual waiver: **`W-CKL-CHARTER-MRS`** (platform scope).

## Tile-faithful execution (Cycle 7)

**Decision:** **W-TILE-FAITHFUL remains — NOT cleared.** Cycle 7 inventory found no tile/crop/ROI API in Genblaze (`test_genblaze_tile_api_inventory.py`). Director emits **`execution_mode: full_frame_with_tile_evidence`** with **StagedTileExecutionEvidence** (planning-only; no fake per-tile shade).

**Minimum Genblaze change to clear:** extend `POST /api/engine3d-still` with `crop_region: {x,y,w,h}` (or dedicated tile still route) and Director dispatch loop.

**ADR:** `docs/governance/cecp/trails/idac-stack-2026-07/ADR-002-tile-faithful-blocked-on-genblaze-api.md`

## Agent rule

Waivers may appear in test markers (`xfail`, `skip`) and this table — never as passing Conformance rows.
