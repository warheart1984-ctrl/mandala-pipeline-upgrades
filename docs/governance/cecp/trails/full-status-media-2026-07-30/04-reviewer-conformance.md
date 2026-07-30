# 04 — Reviewer conformance

| Field | Value |
|-------|-------|
| Role | Reviewer |
| lens | Boundary-Guardian + Conformance |
| Verdict | **PASS_WITH_GAPS** |

## Claim ↔ evidence

| Claim | Tag | Evidence |
|-------|-----|----------|
| Engine3D soft-raster film works | **enforced** (host path) | showcase 30s/10s MP4s + raster-upgrade 13/13 |
| OpenCL beauty probe works | **partial** | `opencl-tonga-still.png` radial glow; not scene plate |
| Cycles external-PBR smoke works | **partial** | fresh `01d7230e569e0c04` beauty + prior `587f…` |
| Lemonade SD pixels | **held** / deferred | `lemonadeHeld: true`; CCC `pixelsProduced: false` (prior verification trail) |
| Photoreal Phase 2 evidence emit | **partial** | pep/spr/cec written; scores Partial |
| Photoreal Phase 3 FPEC promote CLI | **declared/missing** | no `promotionPipeline.js`; no npm script |
| Phase 4 CPCS certified | **false** | prior `cpcs.json` `certified:false`; live certify CLI broken |
| Full Photoreal | **forbidden claim** | Drive-G-1 — do not assert |

## Conformance notes

- Governed-render trail status remains `partial` even when Cycles `photorealClaim: true` (plate-level honesty ≠ Full Photoreal).
- Prior CPCS pep/spr (0.8788/1.0) must not be presented as the live re-emit scores (0.6061/0.65).
