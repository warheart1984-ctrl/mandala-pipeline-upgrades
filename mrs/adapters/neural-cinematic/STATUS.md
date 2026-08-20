# Neural Cinematic Engine — Status (honest)

Capability: `neural_cinematic_simulation_backend`  
Schema: `neural-cinematic/0.1`  
Package tag: **partial_with_gaps** (runnable stills + Simulation Chamber flipbook; not a finished movie)

Status vocabulary used in artifacts:

| Tag | Meaning |
|-----|---------|
| `declared` | Contract / stub only — not executable here |
| `declared_stub` | Explicit non-implementation (e.g. photo→SRP) |
| `partial` | Runnable path with known limits |
| `partial_with_gaps` | Runnable path; `gaps: []` lists what is missing |

Every durable artifact should carry an explicit `gaps: []` array (may be empty only when status is purely `declared` and gaps are listed on the organ stub).

## Per-organ status

| Organ / artifact | Status | Gaps (summary) |
|------------------|--------|----------------|
| **SRP** (SceneReconstructionPackage) | `declared_stub` | No monocular depth, normals, segmentation, mesh, or camera solve |
| **Simulation Chamber** (SCW / Motion Organ) | `partial_with_gaps` | Flipbook / Ken-Burns camera metadata only; depth/normal/motion buffers are synthetic stubs; no soft-body, weather engine, or temporal AI video |
| **AI Painter** (SD-Turbo :13305) | `partial_with_gaps` | Bridge/sd-server optional; skip → `beauty_skipped_*`; txt2img not locked img2img; **never** claim photoreal |
| **NCS** (NeuralCinematicSequence) | `partial_with_gaps` | Stills + frameRefs + provenance hashes; not Movie Lane assemble; not Cosmos video paint |
| **AAIS** Factory Workers | `declared` | Worker IDs + notes only; no Mandala AAIS runtime / scheduler |
| **Mythar** Sonic Breath | `declared` | `audioPlan` / `scoreIdentity` hooks only; no TTS/Beatbox synthesis in NCE |
| **Cosmos** | `declared` (optional) | **Not required** (`cosmosRequired: false`); weights not downloaded in this package |
| **Story Forge** | boundary only | Narrative law stays upstream; NCE must not invent `characterId` from filenames |
| **Movie Lane assemble** | `declared` | Final movie assembly is Infinity / Story Forge — not this adapter |

## Gap bullets (operators)

- Simulation Chamber replaces Cosmos Transfer for **local demo motion only**.
- Depth / normal / optical-flow buffers exist as **declared synthetic stubs** (or Ken-Burns camera metadata), not computed geometry.
- AI Painter may apply SD-Turbo via Lemonade `:13305` → sd-server; offline demos use `beauty_skipped_*` and must not fake a beauty pass.
- AAIS/Mythar surfaces are **declared** stubs with `gaps: []` — do not treat worker IDs or scoreIdentity as live runtime proof.
- Provenance on NCS records `capabilityId`, model ids, file sha256 hashes, and intent/world/timeline ids.

## Offline verification

```bash
cd mrs/adapters/neural-cinematic
python -m pytest test_nce.py -q
python demo_pipeline.py --dry-run --frames 4
```
