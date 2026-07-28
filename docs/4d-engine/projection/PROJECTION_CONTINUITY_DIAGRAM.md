# Projection Continuity — Diagram

Status: **declared** documentation · SoT remains JS under `rt4d/`.

```text
                    Intent / Observation Mode preset
                                   │
                                   ▼
                     ┌─────────────────────────┐
                     │  P(θ, φ, τ, κ)  ProjCC  │
                     │  ProjectionKernel       │
                     └────────────┬────────────┘
                                  │ ProjectionState
                                  ▼
                     ┌─────────────────────────┐
                     │ Projector4D (SoT)       │
                     │  π4→3: d4/(d4+w_eff)    │
                     │  π3→2: d3/(d3+z)        │
                     └────────────┬────────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              ▼                   ▼                   ▼
     ApertureFrame3D      PathTracer hooks     HyperCausticLens
     (viewport aperture)  (**declared**)       Verifier (**declared**/
                                               soft-skip OK)
              │
              ▼
        Host viewport / LiveLink
        (≠ CPU RT4D print SoT)
```

## Continuity sketch

```text
  (θ,φ,τ,κ) ──Δsmall──► (θ',φ',τ',κ')
       │                      │
       ▼                      ▼
   screen(p) ──‖Δ‖bound──► screen'(p)   (away from d4+w_eff=0)
```

## Boundary honesty

| Surface | Role |
| --- | --- |
| `output/projector.js` | Print-adjacent math SoT for closed-form projection |
| `projection/*` | Continuity / observation aperture layer |
| CPU RT4D still/print | Sovereign print path — unchanged by ProjCC |
| Vendor GPU assist | Optional acceleration — not required for ProjCC correctness |
