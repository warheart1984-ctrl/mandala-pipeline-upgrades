# Neural Cinematic Engine (Mandala adapter)

Mandala-side **Visual Body** scaffold for cinematic stills + **Simulation Chamber**
motion without Cosmos. Capability id: `neural_cinematic_simulation_backend`.

See [`BOUNDARY.md`](BOUNDARY.md) for the organ map and [`DEMO.md`](DEMO.md) for operators.

## Tree

```text
neural-cinematic/
  BOUNDARY.md              # organ map + hard rules
  DEMO.md                  # RX 580 operator steps
  CAPABILITY.md
  demo-nce.sh
  demo_pipeline.py         # runnable path
  test_nce.py
  contracts/               # SRP, SCW, NCS, NeuralCinematicRequest
  simulation_chamber/      # Motion Organ (skip-Cosmos flipbook)
  ai_painter/              # local SD-Turbo emotion layer
  aais/                    # Factory Worker ID stubs (declared)
  mythar/                  # Sonic Breath audioPlan hooks (declared)
  nce/                     # validate + hashing
  fixtures/                # generated 64² keyframe on demand
  outputs/                 # gitignored run artifacts
```

## Status (honest)

| Artifact / organ | Status |
|------------------|--------|
| SRP | `declared_stub` |
| SCW / Simulation Chamber flipbook | `partial` |
| NCS stills package | `partial` |
| AI Painter (SD-Turbo) | `partial_with_gaps` |
| AAIS workers | `declared` stubs |
| Mythar audio | `declared` boundary |
| Cosmos | `declared` optional — **not required** |
| Movie Lane assemble | `declared` (Infinity) |

## Quick start

```bash
python -m pytest test_nce.py -q
python demo_pipeline.py --dry-run
```
