# 06 — Engineer Standards (ship gate)

**Trail:** `judge-wow-2026-07`  
**Stage:** Engineer Standards  
**Status:** complete  
**Predecessor:** `05-inspector-acceptance.md` (PASS_WITH_GAPS)  
**Also noted:** Reviewer PASS_WITH_NOTES; foreman post-Inspector wow visibility retune  
**Date:** 2026-07-27  
**Role constraint:** read-only (no product/source edits by Standards role)

---

## 1. Verdict: `PASS_WITH_NOTES`

Shipable as a governed composition package. Non-blocking notes on CI coverage,
ops env docs, trail meta freshness, and merge hygiene. No blocking standards,
license, or claim-overreach FAIL.

---

## 2. Standards checklist

| Area | Result | Notes |
|------|--------|-------|
| Coding standards & scope | PASS | ADR compose intent; retunes in-scope; naming/errors match proton package |
| API & contract consistency | PASS | Shared FromField + AOV APIs; Genblaze default-off; no duplicate Scene API |
| Drive-G-1 claim honesty | PASS | Tags match Inspector; trail README refreshed with this stage |
| Drive-G-2 maturity wording | PASS | No bare production-ready; operator vs live Docker distinguished |
| CI / test adequacy | PASS_WITH_NOTES | judgeWow 5/5 local; CI workflow omits proton suite; soft-skip if no dist |
| Docker / ops readiness | PASS_WITH_NOTES | Live Node-in-image **partial**; consider documenting `PROTON_RASTER_*` in `.env.example` |
| Dependency & license hygiene | PASS | No new deps; MIT-compatible reuse |
| No drive-by scope | PASS_WITH_NOTES | Exclude unrelated Genblaze plugin/polish from merge |

---

## 3. Findings

### Blocking
None.

### Notes (non-blocking)
- [medium] `.github/workflows/mrs-rt4d-ci.yml` — does not run `proton/*.test.js`
- [medium] `judgeWow.test.js` soft-skip without engine3d dist
- [medium] Exclude unrelated Genblaze chatgpt_plugin / polish / CORS deltas from this PR
- [low] Document `PROTON_RASTER_*` in Genblaze `.env.example`

---

## 4. Ship gate decision

**Ready to merge/ship as scoped, with listed notes.**

- **Enforced today:** star→proton triptych AOVs, `aovEncode`, Genblaze mocked HTTP, `--scene-spec` CLI, `shadeRasterFragment` hook, P4 `frameSha256`, wow enrich + skipLighting visibility path (`protonCount=50` @256).
- **Partial / declared:** Genblaze live Node-in-Docker, TextureSampler, prompt-string one-shot, bake polish.

---

## 5. Probes cited

- Inspector `05`: proton suite; pytest proton_raster; engine3d raster; demo @256.
- Foreman retune: `judgeWow.test.js` → 5 pass; demo `protonCount=50` beauty/depth/normal.
