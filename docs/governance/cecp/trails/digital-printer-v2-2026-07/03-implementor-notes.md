# 03 — Implementor notes

**Trail:** `digital-printer-v2-2026-07`  
**Role:** Implementor  
**softwareCreationMode:** Constructor + Testwright  
**Status:** §E items implemented on scene-spec print path

## What changed

1. **Denoise (profile-gated, enforced when on)**  
   - `print_hq` / `print_cinematic` / `print_reference`: `denoise=true`  
   - `print_fast`: `denoise=false`  
   - `evidence.py` tags `enforced` when applied; trail id → v2  
   - Provenance via existing BilateralDenoiser in `render-scene.mjs`

2. **Soft penumbra (enforced)**  
   - PrintRequest: `softPenumbra`, `penumbraLightSamples`  
   - qualityOpts patched; render-scene applies `SOFT_PENUMBRA_MIN_RADIUS=0.75`  
   - Evidence + provenance fields

3. **RT4D specular on print path (enforced)**  
   - parse accepts `brdf`/`roughness`/`f0`  
   - convert preserves `materialType: ggx`  
   - render-scene `createMaterial(..., "ggx", …)`

4. **Quality profiles (all enforced)**  
   - All four statusTag=`enforced` with locked dims/spp/depth/knobs

## Tests run (this pass)

| Test | Result |
|------|--------|
| `bilateral-denoise.test.js` | PASS |
| `render-scene-print-quality.test.js` | PASS |
| `soft-penumbra-print.test.js` | PASS |
| `print-specular-ggx.test.js` | PASS |
| `scene-spec.test.js` (13) | PASS |
| `normalization.test.js` (23) | PASS |
| `test_printer_mode.py` | cite when pytest host available |

## Untouched (per foreman)

- Proton Docker dual-layout (`render-proton-splat.mjs`, `run_proton_pipeline.mjs`)  
- Constitutional protected paths  
- No StoryForge imports in Genblaze app
