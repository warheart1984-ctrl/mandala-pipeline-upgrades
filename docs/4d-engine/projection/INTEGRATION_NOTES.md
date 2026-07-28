# ProjCC Integration Notes

| Field | Value |
| --- | --- |
| Status | **partial** (kernel + tests) / path-tracer bind **declared** |
| Contract | [`PROJECTION_CONTINUITY_CONTRACT.md`](./PROJECTION_CONTINUITY_CONTRACT.md) |
| Package | `mrs/packages/renderer-core/src/render/rt4d/projection/` |
| Print SoT | Unchanged — `output/projector.js` + CPU RT4D still/print remain sovereign |

## What is wired (**partial**)

| Surface | Evidence |
| --- | --- |
| `ProjectionState` / `ProjectionKernel` | module + continuity/invariant tests |
| Continuous \(P(\theta,\varphi,\tau,\kappa)\) | `continuityMath.js` aligned with `d4/(d4+w)`, `d3/(d3+z)` |
| Observation presets | `ObservationModePresets.js` + LiveLink policy ids |
| `ApertureFrame3D` | viewport-as-aperture API + tests |
| Hyper-Caustic verifier hooks | factory + structural projection; north-star soft-skip |

## What is **declared** (not fully wired)

| Surface | Note |
| --- | --- |
| `createPathTracerProjectionHooks` | Bundle for future `PathTracer4D.observationProjection` bind |
| v2 path-routing / blend policies | See `OBSERVATION_MODE_RFC.md` |
| GPU-accelerated continuous projection | Vendor assist only — not required for ProjCC correctness |
| Runtime CKL enforcement of PCC invariants | No policy row yet |

## npm scripts

From `mrs/packages/renderer-core`:

```bash
pnpm run test:projection
# or
node --test src/render/rt4d/test/projection.*.test.js
```

## GPU boundary honesty

NVIDIA / AMD / HIP / ROCm skills may advise host/device boundaries. ProjCC does **not**
make vendor GPU the print SoT. Aperture observation ≠ print.

## CECP trail

`docs/governance/cecp/trails/pcc-projection-2026-07/`
