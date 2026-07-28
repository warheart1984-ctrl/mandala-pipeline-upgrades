# 05 — Inspector acceptance

**Trail:** `digital-printer-v2-2026-07`  
**Role:** Inspector (Testwright)  
**InspectorVerdict:** **ACCEPT** for §E closure on scene-spec print path

## Probe matrix (§E)

| Item | Evidence | Tag |
|------|----------|-----|
| Denoise profile-gated | `print_request.py` + `render-scene-print-quality.test.js` PASS + `bilateral-denoise.test.js` PASS | **enforced** (when on) |
| Soft penumbra | `soft-penumbra-print.test.js` PASS; qualityOpts + min radius 0.75 | **enforced** |
| RT4D specular print path | `print-specular-ggx.test.js` PASS; `scene-spec.test.js` ggx convert | **enforced** |
| Quality profiles ×4 | `QUALITY_PROFILES` statusTag enforced; contract 1.2 | **enforced** |
| GGX library regression | `normalization.test.js` 23/23 PASS | **enforced** |

## Residual (not §E — do not hide)

| Item | Tag |
|------|-----|
| Unity / Unreal mesh SHA sync | declared |
| Live CSR / GovernanceDecision emission | declared / skeleton |
| 102 governance suite re-run | declared (not re-run this pass) |
| Denoise on proton/engine3d backends | declared (out of scope) |

## Acceptance

§E gaps from prior HOLD are closed with named tests on the scene-spec print path.
Residual A/C/D items remain — ESFR must not claim PROMOTE_WITHOUT_GAPS.
