# 09 — Promotion request

**Trail:** `digital-printer-v2-2026-07`  
**Request filed:** yes — **PROMOTE_WITH_GAPS** only

## Requested eligibility

~~`PROMOTE_WITHOUT_GAPS` / `PROMOTE`~~ — **denied / not requested** (residual gaps).

**Requested:** `PROMOTE_WITH_GAPS` (ESFR enum) — §E closed; residual A/C/D listed.

## Current eligibility

**`PROMOTE_WITH_GAPS`**

## Closed since prior HOLD (`printer-mode-renderer-2026-07`)

1. Soft penumbra deterministic + tested → **enforced**  
2. RT4D specular print path fixtures → **enforced**  
3. Denoise quality-profile policy + evidence honesty → **enforced** (scene-spec)  
4. All four print quality profiles → **enforced**

## Remaining gaps (explicit)

1. Unity / Unreal / Engine mesh SHA sync — **declared**  
2. Live CSR / GovernanceDecision emission — **declared** / **skeleton**  
3. A-row 102 governance / CKL re-validation — **declared**  
4. Denoise on non–scene-spec backends — scoped out (**declared**)

## What may ship under PROMOTE_WITH_GAPS

- Printer adapter + Genblaze `/printer` HTTP (opt-in execute)  
- Quality profiles + timeout env  
- Profile-gated CPU bilateral denoise + soft penumbra + GGX print-path materials  

Promotion to empty-gap `PROMOTE` / user-language PROMOTE_WITHOUT_GAPS requires closing
or permanently scoping residual gaps with checklist downgrades.
