# Neural Cinematic Engine — Organ Boundary

> **Capability:** `neural_cinematic_simulation_backend`  
> **Package status:** **partial** scaffold (stills + Simulation Chamber flipbook).  
> **Not** a Story Forge / Movie Lane rebuild. **Not** Cosmos-required.

## Canonical organ map

| Organ | Role | Ownership | This package |
|-------|------|-----------|--------------|
| **Story Forge** | Narrative Law | Infinity | Boundary only → [`../storyforge-boundary/`](../storyforge-boundary/) (contract 1.1). Do **not** rebuild Movie Lane / Scene Archive / Visual Lane here. |
| **Mandala** | Visual Body | This repo | Renderers, sim hooks, cameras, reconstruction stubs, AI Painter, this NCE adapter. |
| **Mythar** | Sonic Breath | In-repo encoder + external SRE/TTS | [`mythar/`](mythar/) accepts `audioPlan` / `scoreIdentity` hooks; does **not** synthesize ritual audio. |
| **AAIS** | Factory Workers | External / AIKI optional provider | [`aais/`](aais/) worker ID stubs + enforcement notes only. No Mandala AAIS runtime. |
| **Mandala Simulation Chamber** | Motion Organ | This package | [`simulation_chamber/`](simulation_chamber/) — **local Cosmos replacement** for demo motion (camera-path flipbook). |
| **Cosmos** | Optional rented NVIDIA polish | External | **Declared optional.** Never required for local RX 580 demo. Do not download weights in this PR. |
| **Movie Lane assemble** | Final Movie | Infinity / Story Forge | **Declared** — NCE emits NCS evidence; assembly stays upstream. |

## Final flow (expression chain)

```text
Story Forge (narrative truth)
  → Mandala (visual body / reconstruction stub)
  → Mythar (sonic breath hooks — declared)
  → AAIS (factory worker ids — declared stubs)
  → Simulation Chamber (motion organ — partial flipbook)
  → AI Painter (SD-Turbo local — partial_with_gaps)
  → NeuralCinematicSequence (NCS)
  → Final Movie assemble (Movie Lane — declared on Infinity)
```

## Hard rules

1. **Narrative truth** is owned by Story Forge / Infinity. NCE expresses visually; it cannot change who lived/died or invent `characterId` from filenames.
2. **AAIS-style evidence:** external model ids (e.g. `SD-Turbo`) and worker ids are recorded on the NCS; models stay behind adapters.
3. **Simulation Chamber replaces Cosmos Transfer for local demo motion.** Cosmos remains an optional sidecar later.
4. **SRP** (photo→depth/mesh) is `declared_stub`. Full physics / weather engines are **declared**, not built here.
5. Do not put NVIDIA API keys in the repo. Do not edit constitutional charter files for this scaffold.

## Compatible identity fields

When present, `characterId` / `identityLock` follow `storyforge-mandala-contract/1.1` keys
(`species`, `faceRefId`, `bodyBuild`, `armorId`, `weaponId`, `weaponHeldIn`, …).
Absence is honest; invention from image basenames is refused.
