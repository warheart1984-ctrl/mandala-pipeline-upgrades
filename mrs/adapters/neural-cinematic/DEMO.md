# NCE Demo — Simulation Chamber (no Cosmos)

Operator steps for the **partial** Neural Cinematic Engine path on AMD RX 580.
Style mirrors `mrs/apps/rt4d-chatgpt-plugin/demo-warrior.sh`.

## What this demo is / is not

| Claim | Status |
|-------|--------|
| Keyframe → optional SD-Turbo AI Painter → Simulation Chamber flipbook → NCS JSON + sha256 | **partial** |
| Camera path templates (`orbit` / `push-in` / `close-up`) with per-frame camera metadata | **partial** |
| Photo→SRP depth/normals/mesh | **declared_stub** |
| Soft-body / weather physics | **declared** |
| Temporal AI video / Cosmos Transfer | **declared optional — skipped** |
| Story Forge Movie Lane assemble | **declared** (Infinity) |
| Mythar live chant/TTS | **declared** boundary (`scoreIdentity` hook only) |

Story Forge contract: [`../storyforge-boundary/`](../storyforge-boundary/) (v1.1).  
Organ map: [`BOUNDARY.md`](BOUNDARY.md).

## Warrior press-Play short

Identity-locked courtyard flipbook from storyforge-boundary fixture:

```bash
bash demo-short-warrior.sh
# or
python3 demo_short_warrior.py --out-dir ./outputs --frames-per-shot 4
```

Produces `press-play.mp4` tagged `flipbook-not-motion` (click bed ≠ Beatbox score).
S01 `characterStateHash` / `scoreIdentity` must equal S08.


| Port | Service | Role |
|------|---------|------|
| `:13305` | sd-bridge | AI Painter OpenAI-schema → SD-Turbo |
| `:13306` | sd-server | Vulkan SD-Turbo 512² (1024 OOMs) |
| — | Cosmos | **Not used** |

## Commands

From repo root (or this package):

```bash
# Contract tests — no GPU
cd mrs/adapters/neural-cinematic
python -m pytest test_nce.py -q

# Dry-run demo (always works offline)
python demo_pipeline.py --dry-run --frames 8 --camera-path orbit

# Or wrapper (probes bridge; continues if down)
bash demo-nce.sh
bash demo-nce.sh --dry-run
```

With optional identity + Mythar score hook (must be supplied — never inferred from PNG name):

```bash
python demo_pipeline.py --dry-run \
  --character-id warrior-anthro-fox-01 \
  --species anthro \
  --score-identity courtyard-warrior-theme-v1 \
  --camera-path push-in \
  --frames 8
```

Outputs land under `outputs/nce-run-<UTC>/`:

- `01-painted.png` — AI Painter result or copy (`beauty_skipped_bridge_down` if bridge down)
- `sim_frames/*.png` — Simulation Chamber flipbook
- `srp.declared_stub.json` — reconstruction stub
- `scw.json` — SimulatedCinematicWorld (**partial**, `cosmosRequired: false`)
- `ncs.json` — NeuralCinematicSequence with hashes + organ status map
- `summary.json` — operator-facing status table

## Honesty labels in JSON

- `beautyStatus`: `beauty_applied_sd_turbo` | `beauty_skipped_bridge_down` | `beauty_skipped_dry_run` | …
- `painterStatus`: `partial_with_gaps`
- `organs.cosmos`: `declared_optional_skipped`
- `organs.simulationChamber`: `partial_flipbook`
- `organs.movieLaneAssemble`: `declared_infinity`
