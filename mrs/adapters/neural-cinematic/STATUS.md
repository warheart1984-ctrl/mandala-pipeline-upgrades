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

## End-to-end operators (book → press Play)

```bash
cd mrs/adapters/neural-cinematic
python3 infinity_bridge.py          # Infinity clone + warrior parity
bash demo-short-warrior.sh          # fixture short MP4
bash demo-book-drop.sh              # Archive Ch1 excerpt heuristic → MP4
python3 audio_handoff.py            # Mythar/Beatbox probe (declared/partial)
python3 quality_probe.py            # sculpt/Daniel/Cosmos ladder
```

Infinity root: `/media/jon/New Volume/Project Infinity` (`INFINITY_ROOT`).
Book-drop shots from markdown are **heuristic** until `--build-json` from Story Forge Movie Lane.

## Live Story Forge + ZBrush production intake

```bash
cd mrs/adapters/neural-cinematic
python3 import_zbrush_production.py --character-id warrior-anthro-fox-01   # ensure drop folder
# Drop ZBrush sculpt.obj into packages/sovereign-sculptor/production/warrior-anthro-fox-01/
python3 import_zbrush_production.py --character-id warrior-anthro-fox-01 --mesh /path/to/sculpt.obj
python3 emit_storyforge_build.py --out outputs/live-build.json
python3 demo_from_build.py --build-json outputs/live-build.json
# or: bash demo-live-sf.sh
```

| Surface | Status | Notes |
|---------|--------|-------|
| `emit_storyforge_build.py` | `partial_with_gaps` | Live Infinity `StoryForgeBackendPipeline` + Mandala enrichment (`identityLock` operator/sculpt) |
| `sculpt_under_lock.py` | `partial_with_gaps` / fixture | `productionSculpt=true` **only** when OBJ/FBX present; else fixture + honest tag |
| Blender preview bake | `partial_with_gaps` | Workbench 384², low-memory settings — **not** lookdev |
| SD-Turbo beauty | `partial_with_gaps` | **512² only** on RX 580 (~8GB VRAM); no Cosmos |

**Hardware honesty:** System RAM is whatever was already working before any upgrade attempt (do **not** document 32GB). Extra stick DOA does not change VRAM limits.
