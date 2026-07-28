# ESFR Promotion Checklist — Digital Printer Initiative

> **Status:** living checklist with honest Drive-G-1 tags.  
> **Active trail verdict:** `docs/governance/cecp/trails/digital-printer-v2-2026-07/08-esfr-verdict.json`  
> **Prior HOLD:** `docs/governance/cecp/trails/printer-mode-renderer-2026-07/08-esfr-verdict.json`  
> **Do not** request `PROMOTE_WITHOUT_GAPS` while residual gaps remain.

Legend: `[x]` verified this initiative · `[ ]` open / unverified · tags:
**enforced** / **partial** / **declared** / **skeleton**

## A. Governance Completeness

| Item | Box | Tag |
|------|-----|-----|
| 102/102 governance tests passing | [ ] | declared (not re-run this pass) |
| CHARTER frozen | [x] | enforced |
| CONTRACTS frozen | [x] | enforced |
| CKL decision logic validated | [ ] | declared |
| Governance Kernel intent evaluation validated | [ ] | declared |
| CSE execution + CSR provenance validated | [ ] | declared (CSR skeletal) |
| Schemas created (GovernanceDecision, CSR, ProvenanceFrame) | [x] | partial |

## B. Rendering Determinism

| Item | Box | Tag |
|------|-----|-----|
| Deterministic sampling (stratified AA) | [x] | enforced |
| Deterministic reconstruction | [x] | enforced (profile-gated BilateralDenoiser) |
| Deterministic tonemap (ACES opt-in) | [x] | enforced |
| Deterministic color pipeline | [x] | enforced |
| Deterministic encode → PNG | [x] | enforced |
| Deterministic hash generation | [x] | enforced |
| Print plate reproducible across runs | [x] | partial |

## C. Surface Sovereignty

| Item | Box | Tag |
|------|-----|-----|
| Surface contract enforced | [x] | enforced |
| Error states enforced | [x] | enforced |
| Evidence hashes generated | [x] | enforced |
| Lineage generated | [x] | enforced |
| Unity + Unreal + Engine surfaces synced | [ ] | declared |
| Mesh SHA-256 verification | [ ] | declared |

## D. Evidence Completeness

| Item | Box | Tag |
|------|-----|-----|
| beauty.png | [x] | enforced |
| evidence.json | [x] | enforced |
| lineage.json | [x] | enforced |
| provenance frames | [x] | partial |
| CSR records | [x] | declared |
| governance decision logs | [ ] | skeleton |

## E. Gaps to Close Before Promotion

| Item | Box | Tag |
|------|-----|-----|
| Denoise → enforced | [x] | enforced (profile-gated; scene-spec) |
| Soft penumbra → enforced | [x] | enforced |
| RT4D specular materials → enforced | [x] | enforced (print path) |
| Print timeout governance → added | [x] | enforced (`MRS_PRINT_TIMEOUT_SECONDS`) |
| Print quality profiles → added | [x] | enforced (all four) |

## Verdict

**ESFRVerdict:** `PASS_WITH_GAPS`  
**PromotionEligibility:** `PROMOTE_WITH_GAPS`  
(User-language **PROMOTE_WITHOUT_GAPS** is **not** authorized while A/C/D residuals remain.)
