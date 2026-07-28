# 06 — Engineer Standards (ESFR)

**Trail:** `printer-gpu-quality-speed-2026-07`  
**Stage:** ESFR  
**Status:** **declared** design initiative  
**Inspector input:** PASS (design) / GPU runtime not ready

## ESFRVerdict

| Field | Value |
|-------|-------|
| Verdict | **PASS_WITH_GAPS** (docs/design only) |
| PromotionEligibility | **HOLD** |
| equivalentUserLanguage | HOLD — do not ship GPU print backend |
| residualGaps | GPU backend; parity fixtures; quality-per-sample metric exporter; CUDA/HIP absent; AMD/NVIDIA MCP not installed |

## Why HOLD (not REJECT)

- Design is coherent, evidence-bound, and respects sovereignty.
- Gaps are intentional (no implementation this pass), not constitutional violations.
- REJECT would apply if design claimed NIM as print SoT or invented AMD support — it does not.

## Test matrix (probes — design citations only)

| Probe | Result | Cite |
|-------|--------|------|
| 01 Intent declared | PASS | 01-architect-adr.md |
| 02 Boundary / bans | PASS | BOUNDARY.md + sovereignty.py referenced |
| 03 Determinism preserved | PASS (design) | seed + profiles + parity gate |
| 04 Evidence chain | PASS (design) | no removal of provenance fields |
| 05 No fake free lunch | PASS | Approaches A–C tradeoffs |
| 06 NVIDIA compatibility | PASS (assist≠SoT) | Genblaze vs printer |
| 07 AMD honesty | PASS | absent |
| 08 Runtime GPU tests | SKIP / HOLD | no code |

## Relation to Digital Printer v2.0

v2 trail remains **PROMOTE** / **PROMOTE_WITHOUT_GAPS**. This trail does **not** reopen v2 gaps.

## Next promotion path

1. User approves design spec  
2. Implementor executes plan tasks (quality-per-sample → parity → optional webgpu flag)  
3. Re-run Inspector + ESFR; only then consider PROMOTE_WITH_GAPS for GPU path
