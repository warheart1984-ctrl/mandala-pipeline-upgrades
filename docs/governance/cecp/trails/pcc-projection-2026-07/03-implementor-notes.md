# 03 — Implementor notes

| Field | Value |
| --- | --- |
| `mode` | Physicist |
| `softwareCreationMode` | Constructor + Testwright |
| Status | **partial** |

## What shipped

1. Continuous \(P\) with \(\tau\) as \(w\)-offset, \(\kappa\) as soft d4 scale (identity at 0),
   \(\theta,\varphi\) as post-project view orientation.
2. Fidelity at zero params ≡ `Projector4D` / `classic4Dto3D`.
3. Observation presets mapping LiveLink policy ids.
4. `ApertureFrame3D` with `role: observation_aperture`.
5. Hyper-Caustic verifier: factory + structural projection + north-star soft-skip.
6. Path-tracer hooks explicitly `wiredIntoPathTracer4D: false`.

## Tests

```bash
cd mrs/packages/renderer-core
pnpm run test:projection
# 20/20 pass (2026-07-28)
```

## Series mapping (01–10)

| Step | Artifact |
| --- | --- |
| 01 | PCC docs + ProjectionState + kernel |
| 02 | pccInvariants |
| 03 | HyperCausticLensVerifier |
| 04 | continuityMath |
| 05 | ObservationModePresets |
| 06 | ApertureFrame3D |
| 07–09 | projection.*.test.js |
| 10 | INTEGRATION_NOTES + pathTracerHooks + CECP + ESFR |

## Regressions preserved

- `Projector4D` formulas unchanged
- `createHyperCausticLens` factory untouched in behavior
- CPU print path not redirected through aperture
