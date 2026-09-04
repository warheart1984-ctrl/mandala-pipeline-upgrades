# Mandala RT4D Pipeline Upgrades: Organic Environments

**Start here:** [`docs/START_HERE_MRS_30_MIN.md`](docs/START_HERE_MRS_30_MIN.md) — practical onboarding in ~30 minutes (commands, layout, role paths). Not marketing.

## Quick Start (30 seconds)

```bash
# Clone and install
git clone <repo-url> && cd "Mandala Rendering Software"
npm install

# One prompt → governed soft-raster still + verification trail
npm run mrs:governed-render -- --prompt "dim room soft light, human at table"
# → tmp/governed-render/<runId>/still.png + verification-trail.json
# (Engine3D soft-raster layout; Lemonade held; not photoreal — see docs/4d-engine/PHOTOREAL_PROVIDER_STRATEGY.md)
# optional: --beauty remote  → select photoreal.remote.diffusion (deferred stub if URL unset)
# optional: --beauty external-pbr → GLB export Held; Cycles beauty if BLENDER_PATH / Blender on PATH

# Run the web demo
npm run serve
# open http://localhost:8080

# Run all tests (smoke + governance + conformance)
npm run test:all

# Run governance tests only
npm run test:governance

# Sync surface meshes to Unity/Unreal
npm run sync:surfaces

# Render a still frame
npm run render:4d -- --surface tesseract --width 512 --height 512
```

Published title: **4D Rendering System v1.0**  
Formal engine name: **RT4D** (*Ray Tracer for Four Dimensions*)  
Official validation scene: **Hyper-Caustic Lens**

1. **Instanced Grass Geometry** - GPU-driven blade rendering with wind simulation
2. **Animal Shell Fur** - DQS normal extrusion with alpha-noise hair strands
3. **Terrain Heightmap Integration** - Ground plane snapshots for both systems

**Namespace:** `SovereignX.CIEMS.Engine.*`  
**Evidence bound:** status tags (`enforced` / `partial` / `declared` / `skeleton` / `held` / `blocked`) follow [`constitution/CHARTER.md`](constitution/CHARTER.md) and machine SoT in [`engine/constitution/charter.js`](engine/constitution/charter.js) — do not treat prose alone as a runtime gate. Drive-G-1: soft-raster ≠ photoreal; no Full Photoreal / Phase 4 certified claims without CPCS `certified: true`.

## Current standings (2026-07-30)

Operator snapshot after `feat/pcc-projection-continuity` / [PR #89](https://github.com/warheart1984-ctrl/Mandala-Rendering-System-MRS-/pull/89). Details: [`docs/governance/cecp/trails/full-status-media-2026-07-30/STANDINGS.md`](docs/governance/cecp/trails/full-status-media-2026-07-30/STANDINGS.md) · quality log: [`docs/4d-engine/QUALITY_PROGRESS_LOG.md`](docs/4d-engine/QUALITY_PROGRESS_LOG.md).

| Lane | What works | Status |
| --- | --- | --- |
| Engine3D soft-raster | Governed one-command stills; cinematic-v2 DOF/MB/dust/grade; Amendment VII apply | **enforced** host path · **not photoreal** |
| Photoreal external-PBR | SceneSpecification → GLB (**held**) → Blender Cycles beauty when Blender present | **partial** · plate `photorealClaim` when pixels written · **not** Full Photoreal |
| Prod face fixture → Cycles | `HumanFaceRiggedProd.glb` default (~752 KB, ~10k tris); `face_pipeline.py --scene-type face\|tesseract` | **partial** face beauty · **not** Full Photoreal |
| Cycles device (this host) | Blender 5.2 Cycles; no OpenCL; R9 380 no HIP → script falls back **CPU-only** | **partial** · honest CPU path |
| Face GLB validation | `eyes` material + `TEXCOORD_0` in build scripts; validator clean on prod + CI fixtures | **enforced** (zero warnings on checked assets) |
| Photoreal evidence (PEP/SPR/CEC/CPCS) | Phase 2 emit + promote/certify CLIs restored; CPCS remains honest-incomplete | **partial** · `certified: false` · Phase 4 **forbidden** |
| OpenCL / CL-Gen | ImageGen cascade + Tonga still probe | **partial** · probe ≠ scene plate |
| Lemonade SD | Local diffusion beauty | **held** (`pixelsProduced: false` on this host class) |
| Conformance | Browser profile + CSR governance-trace check | **enforced** `17/17` via `npm run test:conformance` |

## What’s new (2026-07)

Operator-facing deltas only — not a promotion claim. Evidence lives in code, tests, and CECP trails.

| Area | What landed | Status |
| --- | --- | --- |
| Governance / conformance | CSR governance-trace check in default profile; browser Node fetch stub; runtime provenance in CI | **enforced** `17/17` + `npm run test:runtime-provenance` |
| Engine3D biometric / world profiles | Amendment VII biometric gates + Amendment VIII world-profile foundation (`world.biogeometric` …) | VII **enforced** (opt-in) · VIII **partial** — [`docs/4d-engine/WORLD_PROFILE_BIOGEOMETRIC.md`](docs/4d-engine/WORLD_PROFILE_BIOGEOMETRIC.md) |
| Photoreal path + CCC-ImageGen | `photoreal.external.pbr` / `photoreal.remote.diffusion`; CCC honesty select; GLB→Cycles evidence | **partial** · Lemonade **held** — [`docs/4d-engine/PHOTOREAL_PROVIDER_STRATEGY.md`](docs/4d-engine/PHOTOREAL_PROVIDER_STRATEGY.md) · [`docs/4d-engine/CCC_IMAGE_GEN.md`](docs/4d-engine/CCC_IMAGE_GEN.md) |
| Prod face fixture + scene variety | `build-prod-face-fixture.mjs` → `HumanFaceRiggedProd.glb`; Genblaze `face_pipeline.py --scene-type face\|tesseract` (tesseract via `render-glb`→Cycles) | **partial** · validation clean · face quality **not** Full Photoreal |
| Cycles host honesty | `render-glb-cycles.py` prefers GPU backends; falls back CPU when OptiX/CUDA/HIP unavailable (Blender 5.2 / R9 380 class) | **partial** · CPU-only on this host |
| Sovereign X AMD legacy-efficient | `gpu.compute.amd.legacy_efficient` lane (algo/mem/gov); OpenCL still + HIP stubs | **partial** · HIP device run often **blocked** — [`docs/4d-engine/PHOTOREAL_ON_R9_380.md`](docs/4d-engine/PHOTOREAL_ON_R9_380.md) |
| Genblaze BYOK + lanes | Local-first keys; render lanes + deploy health; NIM/GPU **assist-only** | **partial** — [`docs/genblaze/`](docs/genblaze/) |
| ChatGPT app + Jarvis | Native pipeline tools; Jarvis session autopersist / Continuity Ledger hooks | **partial** — [`mrs/apps/chatgpt-mrs/`](mrs/apps/chatgpt-mrs/) · [`jarvis-memoryboard/`](jarvis-memoryboard/) |
| AIKI scaffold | Top-level `aiki/` CKO / Mission Lock / IPI scaffold | **skeleton** / constitution **declared** — [`aiki/README.md`](aiki/README.md) |
| Mandala agent pack | 14-agent corpus → 6 Cursor agents + Mandala Mode; lint/radar/auto-fix | **declared** / **partial** — [`docs/governance/cecp/MANDALA_SIX_AGENTS.md`](docs/governance/cecp/MANDALA_SIX_AGENTS.md) |
| GPU modules | `PostProcessor` / `ShadowMapper` / `EnvironmentMapper` + ESM `GPUPreviewClient` | **partial** — unit tests under `mrs/packages/renderer-core/test/gpu/` |
| Digital Printer / Sovereign X | CPU RT4D print SoT (`cpu.rt4d.print`); GPU/NIM assist ≠ print beauty SoT | **partial** — see [Sovereign X · Digital Printer](#sovereign-x--digital-printer) |

## Showcase (reference surfaces)

Interactive Canvas demo and tutorials for the five registered surfaces — **reference implementation** showcase, not a claim of product-complete post-processing.

| Entry | Path |
| --- | --- |
| Web demo | [`examples/web-demo.html`](examples/web-demo.html) |
| Gallery | [`examples/gallery/`](examples/gallery/) |
| Tutorials | [`examples/tutorials/`](examples/tutorials/) |
| Suite index | [`examples/README.md`](examples/README.md) |

```bash
npm run serve
# open http://localhost:8080/examples/web-demo.html
```

Package notes: [`4d-renderer/README.md`](4d-renderer/README.md) (shim) · canonical core: [`mrs/packages/renderer-core`](mrs/packages/renderer-core) (`@mrs/renderer-core`).

**MRS × ChatGPT App (monorepo):** see [`mrs/README.md`](mrs/README.md) and [`mrs/apps/chatgpt-mrs/README.md`](mrs/apps/chatgpt-mrs/README.md).

### Related surfaces (honest pointers)

| Surface | Path | Status |
| --- | --- | --- |
| Genblaze media (FLUX stills → B2) | [`mrs/apps/genblaze-media`](mrs/apps/genblaze-media) | **partial** operator MVP; render lanes wired; video **default off**; BYOK under [`docs/genblaze/`](docs/genblaze/) |
| NIM Cosmos / Seedance video | same app, opt-in backends | Cosmos + Seedance (fal, **billed**) — temporal layers **declared** |
| ChatGPT MRS + Jarvis tools | [`mrs/apps/chatgpt-mrs`](mrs/apps/chatgpt-mrs) · [`jarvis-memoryboard/`](jarvis-memoryboard/) | **partial** — Continuity Ledger at `:8001`; not full RT4D viewport |
| AIKI (knowledge infra) | [`aiki/`](aiki/) | **skeleton** scaffold · Mission Lock / CKO-0001 path — not MRS runtime |
| CCC-ImageGen | [`docs/4d-engine/CCC_IMAGE_GEN.md`](docs/4d-engine/CCC_IMAGE_GEN.md) · `sovereign-x/governance/ccc-image-gen.json` | **partial** honesty select; Lemonade beauty **held** |
| SX AMD legacy-efficient | [`docs/4d-engine/PHOTOREAL_ON_R9_380.md`](docs/4d-engine/PHOTOREAL_ON_R9_380.md) | **partial** lane · OpenCL probe · HIP often **blocked** |
| Mandala agent pack | [`mandala-agent-pack/`](mandala-agent-pack/) | **declared** / **partial** — 14 corpus → 6 Cursor agents; see [Mandala agents](#mandala-agents--tooling) |
| CROS scaffold | [`mrs/packages/cros`](mrs/packages/cros) | Reference architecture — CI-001..006 validators **caller-invoked**; **not** a claim genblaze implements CROS |
| PI-* / cross-runtime / CKL soft·enforce | [`mrs/packages/renderer-core`](mrs/packages/renderer-core) · [`STACK.md`](mrs/packages/renderer-core/src/render/rt4d/invariants/STACK.md) | PI-* **tested**; soft accept opt-in; enforce deny opt-in |
| SX-PTIG (continuity ≠ acceptance) | [`SX-PTIG.md`](mrs/packages/renderer-core/src/gpu/constitution/SX-PTIG.md) | **Declared** + unit-tested heuristics; not full CKL enforcement of PTIG |
| Desktop copilot shell | [`desktop/`](desktop/) | Chat / tools / probes — **not** a full RT4D viewport |

```bash
cd mrs && pnpm run setup   # fresh clone: install + rebuild canvas/esbuild
```

## Genblaze BYOK (local-first)

Genblaze is a **concept media** operator surface (2D FLUX/NIM stills → B2 provenance), not a 4D renderer. BYOK keeps secrets in the browser tab.

| Rule | Evidence |
| --- | --- |
| Keys in `sessionStorage` only (tab lifetime) | UI + [`app/byok.py`](mrs/apps/genblaze-media/app/byok.py); charter |
| Hosted BYOK off unless `GENBLAZE_ALLOW_BYOK=1` | Config + unit tests (`tests/test_byok.py`) |
| NIM / GPU / face-assist = **assist-only** | Never Digital Printer / `cpu.rt4d.print` beauty SoT |
| RT4D CPU print remains SoT for plates | [`CONTRACT_DIGITAL_PRINT.md`](mrs/adapters/storyforge-boundary/CONTRACT_DIGITAL_PRINT.md) |

**Docs (operators):**

| Doc | Path |
| --- | --- |
| Onboarding | [`docs/genblaze/operators/user-onboarding-guide.md`](docs/genblaze/operators/user-onboarding-guide.md) |
| Training | [`docs/genblaze/operators/operator-training-manual.md`](docs/genblaze/operators/operator-training-manual.md) |
| Handbook | [`docs/genblaze/operators/operator-handbook.md`](docs/genblaze/operators/operator-handbook.md) |
| BYOK security charter | [`docs/genblaze/security/byok-security-charter.md`](docs/genblaze/security/byok-security-charter.md) |
| Assisted pipeline | [`docs/genblaze/pipeline/byok-assisted-pipeline.md`](docs/genblaze/pipeline/byok-assisted-pipeline.md) |
| App README | [`mrs/apps/genblaze-media/README.md`](mrs/apps/genblaze-media/README.md) |
| Scorecard | [`docs/scorecards/genblaze-media.md`](docs/scorecards/genblaze-media.md) |

```bash
# Local Genblaze (from repo root; Node 20+ + Python venv per app README)
npm run genblaze:media
# UI http://127.0.0.1:8787/  ·  health http://127.0.0.1:8787/health

cd mrs/apps/genblaze-media && pytest -q
```

## Mandala agents · tooling

Constitutional agent lawbook: [`AGENTS.md`](AGENTS.md).

**Shared agent SoT:** [`mandala-agent-pack/`](mandala-agent-pack/) (tracked).  
**`.cursor/` is local IDE config** — gitignored; regenerate operational agents/rules from the pack ([`mandala-agent-pack/docs/cursor-local-setup.md`](mandala-agent-pack/docs/cursor-local-setup.md)). Optional Mandala Mode rule may live at `.cursor/rules/mandala-mode.mdc` locally (lenses only — not a charter rewrite).

| Artifact | Role | Status |
| --- | --- | --- |
| [`mandala-agent-pack/`](mandala-agent-pack/) | 14-agent folders + manifests (skills, personality, Mandala Mode) + lint/radar/auto-fix | **declared** / **partial** |
| `.cursor/agents/` (local) | Six operational Cursor agents (fold of the 14) — **not** git SoT | **partial** / local |
| [`docs/governance/cecp/MANDALA_SIX_AGENTS.md`](docs/governance/cecp/MANDALA_SIX_AGENTS.md) | 14→6 map, mode matrix, hand-offs | **declared** |
| Skill catalogs | `mandala-agent-pack/manifests/skills.json` (~173 IDs landed); fuller inventory **declared** in [`docs/governance/AGENT_SKILL_SPEC.md`](docs/governance/AGENT_SKILL_SPEC.md) | catalogs ≠ executable `SKILL.md` count |
| Release versions | [`docs/governance/RELEASE_VERSIONING.md`](docs/governance/RELEASE_VERSIONING.md) · `npm run release:check` | **partial** |

**Tooling** (CI-backed paths under the pack; heuristics are **partial**, not full constitutional enforcement):

| Tool | Command | Notes |
| --- | --- | --- |
| Constitutional linter | `node mandala-agent-pack/lint/run-lint.js` | Report / fail on heuristic hits |
| Drift radar | `node mandala-agent-pack/drift-radar/generate-report.js` | JSON report artifact |
| Auto-fix | `node mandala-agent-pack/auto-fix/auto-fix.js` | **Dry-run** default; refuses protected paths; CI never `--apply` |
| Additive CI | [`.github/workflows/mandala-agent-ci.yml`](.github/workflows/mandala-agent-ci.yml) | Lint + radar + dry-run + governance/conformance/runtime + Genblaze BYOK pytest |

Root [`.github/workflows/ci.yml`](.github/workflows/ci.yml) remains the primary smoke/governance/conformance pipeline; Mandala Agent CI is **additive**.

## Sovereign X · Digital Printer

Authoritative print beauty / evidence SoT is **CPU RT4D** (`cpu.rt4d.print`). GPU integrators, WebGPU preview, Genblaze NIM, and AMD legacy-efficient assists are **assist-only** — they must not be claimed as print SoT.

| Doc | Path |
| --- | --- |
| Printer HTTP contract | [`docs/governance/cecp/PRINTER_SERVICE_API.md`](docs/governance/cecp/PRINTER_SERVICE_API.md) (**partial**) |
| Digital print boundary | [`mrs/adapters/storyforge-boundary/CONTRACT_DIGITAL_PRINT.md`](mrs/adapters/storyforge-boundary/CONTRACT_DIGITAL_PRINT.md) |
| AMD legacy-efficient lane | [`docs/4d-engine/PHOTOREAL_ON_R9_380.md`](docs/4d-engine/PHOTOREAL_ON_R9_380.md) · trail [`sx-legacy-efficient-3layer-2026-07`](docs/governance/cecp/trails/sx-legacy-efficient-3layer-2026-07/) (**partial**) |
| CCC-ImageGen | [`docs/4d-engine/CCC_IMAGE_GEN.md`](docs/4d-engine/CCC_IMAGE_GEN.md) (**partial**; Lemonade SD **held**) |
| Printer-mode trail | [`docs/governance/cecp/trails/printer-mode-renderer-2026-07/`](docs/governance/cecp/trails/printer-mode-renderer-2026-07/) |
| GPU assist / vendor router trails | [`docs/governance/cecp/trails/sovereign-x-gpu-assist-2026-07/`](docs/governance/cecp/trails/sovereign-x-gpu-assist-2026-07/), [`docs/governance/cecp/trails/sovereign-x-vendor-router-2026-07/`](docs/governance/cecp/trails/sovereign-x-vendor-router-2026-07/) |

Initiative ESFR for printer-mode remains **HOLD** / gap-tracked in trail evidence — not marketed as promote-ready.

### Windows native canvas (optional for widget)

Headless PNG (CLI, gallery, some exports) needs native `canvas` + VS C++ Build Tools on Windows — see [`mrs/README.md`](mrs/README.md#windows-native-canvas-honest). Browser demo and ChatGPT widget use Canvas2D and do **not** require cairo.

## Capability snapshot

Statuses below match charter evidence (not marketing). Details: [`constitution/CHARTER.md`](constitution/CHARTER.md) · machine SoT: [`engine/constitution/charter.js`](engine/constitution/charter.js). Per-dimension scorecards: [`docs/scorecards/`](docs/scorecards/). Standings trail: [`full-status-media-2026-07-30`](docs/governance/cecp/trails/full-status-media-2026-07-30/).

| Capability | Status |
| --- | --- |
| 4D parametric surfaces | Present |
| RT4D path rendering | Present |
| Browser host | Present |
| Conformance profile (incl. `csr.governance-trace`) | **Enforced** `17/17` (`npm run test:conformance`) |
| CSSV ledger | Partial |
| Hyper-Caustic Lens validation | Present |
| WebGPU | Present |
| Canvas fallback | Present |
| Engine3D soft-raster + Amendment VII biometric | **Enforced** (opt-in gates) · soft-raster ≠ photoreal |
| Amendment VIII world profiles | **Partial** (`docs/4d-engine/WORLD_PROFILE_BIOGEOMETRIC.md`) · full world engine **not shipped** |
| Photoreal GLB → Cycles (`--beauty external-pbr`) | **Partial** (Held GLB + Cycles when Blender present; CPU-only on R9 380 / Blender 5.2 without HIP) · not Full Photoreal |
| Prod face fixture (`HumanFaceRiggedProd.glb`) + `--scene-type` | **Partial** pipeline default · validator clean · not Full Photoreal face |
| Photoreal evidence PEP/SPR/CEC + promote/certify | **Partial** · CPCS `certified: false` |
| CCC-ImageGen honesty select | **Partial** · Lemonade SD beauty **held** |
| SX `gpu.compute.amd.legacy_efficient` | **Partial** (OpenCL probe; HIP often **blocked**) |
| GPU PostProcessor / ShadowMapper / EnvironmentMapper | Partial (unit-tested modules) |
| Provenance hash + replay lineage receipts | Enforced in runtime unit tests (`npm run test:runtime-provenance`) |
| Genblaze BYOK + render lanes | Partial (app tests + docs) |
| ChatGPT MRS + Jarvis Continuity Ledger | Partial |
| AIKI knowledge scaffold | Skeleton (`aiki/`) |
| Digital Printer `/printer` API | Partial (CPU RT4D print SoT; GPU assist-only) |
| Mandala agent pack + six Cursor agents | Declared / partial |
| Unity adapter | Skeleton (FourDAdapter hybrid-first) |
| Unreal adapter | Skeleton (`unreal/FourDAdapter/`) |
| Native Vulkan dispatch | Experimental |
| Live engine link (shared-frame / MRS↔Unity) | Experimental |
| 4D Inspector (MRS-IC) | Skeleton (contracts v1.1/v1.2 declared; curvature stub) |
| 4D BVH GPU kernels | Skeleton |
| Mathematical substrate / MRS-CRC | Declared |
| 4D physics | Skeleton |
| Shader graph | Skeleton |
| 4D Engine v1 constitution / World Format / PLP | Declared (`docs/4d-engine/v1/`) |
| WorldDocument schema + example validation | Declared / partial (`npm run validate:world-document`) |
| PLP `projectWorld` stub | Skeleton (`@mrs/renderer-core` `/plp`) |
| FourDRenderer v2.0 architecture / RFCs | Declared / draft (`docs/4d-engine/v2/`) — Phase 1 **docs**; GPU/RHI **roadmap** |
| FourDRenderer v2 Unreal RHI / Nanite / Lumen | Roadmap (not FourDAdapter v1.1) |
| RT4D GPU evolution (v2–v4) | Roadmap / declared (`docs/4d-engine/rt4d/`) — wavefront, denoise, multi-GPU, Vulkan/DX **not implemented** |
| Object storage (B2 S3-compatible) | Declared / operator-configured (`@mrs/storage-b2`, [`docs/ops/BACKBLAZE_B2_S3.md`](docs/ops/BACKBLAZE_B2_S3.md)) — not cloud rendering complete |

### Maturity (Drive-G-2)

Do not collapse readiness to one adjective. Use the five dimensions independently (constitutional model, governance methodology, reference implementation, platform engineering, commercial operations). Scorecards:

| Scorecard | Path |
| --- | --- |
| RT4D | [`docs/scorecards/rt4d.md`](docs/scorecards/rt4d.md) |
| 4D Engine v1 | [`docs/scorecards/4d-engine-v1.md`](docs/scorecards/4d-engine-v1.md) |
| FourDRenderer v2 | [`docs/scorecards/fourd-renderer-v2.md`](docs/scorecards/fourd-renderer-v2.md) |
| MRS v2 | [`docs/scorecards/mrs-v2.md`](docs/scorecards/mrs-v2.md) |
| Genblaze media | [`docs/scorecards/genblaze-media.md`](docs/scorecards/genblaze-media.md) |
| AIKI | [`aiki/docs/scorecards/aiki.md`](aiki/docs/scorecards/aiki.md) |

**Hosts:** Browser host is the verified conformance target (`17/17`). Unity / Unreal remain **skeleton** until Play-in-Editor (or equivalent) is proven — adapters are not operator-ready product surfaces.  
**Media honesty:** Engine3D soft-raster and Cycles smoke plates are **partial** evidence paths — not product-complete photoreal or Phase 4 certification.

## v1.0 publish package

| Artifact | Path |
| --- | --- |
| Naming | [`docs/4drs/NAMING.md`](docs/4drs/NAMING.md) |
| Spec | [`docs/4drs/SPEC-v1.0.md`](docs/4drs/SPEC-v1.0.md) |
| Architecture | [`docs/4drs/ARCHITECTURE.md`](docs/4drs/ARCHITECTURE.md) |
| Technical note | [`docs/4drs/First-4D-Renderer.md`](docs/4drs/First-4D-Renderer.md) |
| RT4D API freeze | [`docs/4drs/api/rt4d-v1.0-freeze.md`](docs/4drs/api/rt4d-v1.0-freeze.md) |
| Hyper-Caustic Lens | [`docs/4drs/validation/Hyper-Caustic-Lens.md`](docs/4drs/validation/Hyper-Caustic-Lens.md) |
| Substrate / MRS-CRC | [`docs/4drs/substrate/`](docs/4drs/substrate/) |
| Charter | [`constitution/CHARTER.md`](constitution/CHARTER.md) |
| Citation / Zenodo | [`CITATION.cff`](CITATION.cff), [`.zenodo.json`](.zenodo.json) |
| 4D Engine v1 (declared) | [`docs/4d-engine/v1/README.md`](docs/4d-engine/v1/README.md) |
| FourDRenderer v2 (declared RFCs) | [`docs/4d-engine/v2/README.md`](docs/4d-engine/v2/README.md) |
| FourDRenderer v2 scorecard | [`docs/scorecards/fourd-renderer-v2.md`](docs/scorecards/fourd-renderer-v2.md) |
| RT4D GPU evolution roadmap (v2–v4) | [`docs/4d-engine/rt4d/RT4D_EVOLUTION_ROADMAP.md`](docs/4d-engine/rt4d/RT4D_EVOLUTION_ROADMAP.md) |
| RT4D scorecard | [`docs/scorecards/rt4d.md`](docs/scorecards/rt4d.md) |

### New Source Files
- `mrs/packages/engine3d-core/src/renderer/backend/GpuProfiler.ts` - WebGPU timestamp profiler with `smooth_k = 0.12` EMA

## 1. Instanced Grass Geometry

### Concept
GPU-instanced rendering of millions of grass blades using a single draw call. Each blade is a low-poly quad strip (5 vertices) generated procedurally in the vertex shader. Instance transforms (position, scale, rotation) drive placement and animation.

### Technical Design
- **Storage Buffer**: `GrassInstance` structs packed at `@group(0) @binding(1)` containing `position_xz: vec2<f32>`, `scale: f32`, `rotation: f32`
- **Vertex Shader**: `vs_grass()` generates 5 vertices per blade from `get_blade_vertex(idx)` - tapered strip from base(-0.05) to tip(1.0)
- **Wind Displacement**: `calculate_wind_displacement()` uses scrolling sine waves: `sin(pos.x*1.5 + pos.z*0.8 + time*2.5)`
- **Terrain Heightmap**: Samples `terrain_heightmap` to snap blade bases to ground elevation
- **Fragment Shader**: Linear color gradient from dark roots (`0.08, 0.18, 0.04`) to vibrant tips (`0.42, 0.72, 0.15`)

### Draw Call
```javascript
// Single draw call: 5 vertices per blade × instanceCount
passEncoder.draw(5, instanceCount, 0, 0);
```

### Wind Formula
```wgsl
fn calculate_wind_displacement(pos: vec3<f32>, time: f32) -> vec3<f32> {
    let wave1 = sin(pos.x * 1.5 + pos.z * 0.8 + time * 2.5);
    let wave2 = cos(pos.x * 0.4 - pos.z * 1.2 + time * 1.8);
    let wind_force = vec2<f32>(wave1 + wave2, wave2 * 0.5) * 0.25;
    return vec3<f32>(wind_force.x, 0.0, wind_force.y);
}
```

## 2. Animal Shell Fur via DQS Normal Extrusion

### Concept
Extends Dual Quaternion Skinning (DQS) by extruding concentric "shells" along vertex normals. Fragment pass uses 3D alpha-noise to clip pixels, forming dense fur strands without geometry expansion.

### Technical Design
- **Shell Uniforms**: `@group(1) @binding(0) var<uniform> shell_cfg: ShellUniforms` with `fur_length`, `shell_index`, `total_shells`, `density`
- **Vertex Shader**: `vs_shell_fur()` extrudes vertices along `deformed_normal * extrusion_distance` where `extrusion_distance = (shell_index / total_shells) * fur_length`
- **3D Noise Generator**: `fur_strand_noise(p: vec3<f32>, scale: f32)` uses PCG-like hash: `fract(sin(dot(q, vec3(12.9898, 78.233, 45.543))) * 43758.5453)`
- **Alpha Clipping**: `if (noise < pow(layer_normalized, 1.2)) discard` - creates hair strand pattern
- **Shadowing**: `shadow = mix(0.25, 1.0, layer_normalized)` - darker near skin root

### Multi-Pass Loop
```javascript
for (let i = 0; i < totalShells; i++) {
    // Update shell uniform for layer i
    // Draw animal mesh per concentric shell
    passEncoder.drawIndexed(animalIndexCount, 1, 0, 0, 0);
}
```
ISL intent → CKL/GK decision → TimelinePlayer → Frame provenance → CSSV ledger
                     ↓
            Conformance profile (17 checks per host, incl. csr.governance-trace)
```

- **Engine SoT:** `engine/` — governance, DTOs, runtime (ProvenanceRecorder / ReplayService), CSSV, conformance
- **Browser glue:** `js/` — CSE, boot, renderer (+ Jarvis session autopersist hooks)
- **Renderer core:** `mrs/packages/renderer-core/` — RT4D math/path + Engine3D + GPU assist + photoreal evidence emitters
- **CSSV ledger:** `cssv/` — artifacts.json + transitions.ndjson + frames.ndjson
- **Genblaze:** `mrs/apps/genblaze-media/` — concept media + BYOK + lanes + `/printer` (**partial**)
- **Sovereign X:** `sovereign-x/` — capability router, CCC-ImageGen, AMD legacy-efficient lane (**partial**)
- **AIKI:** `aiki/` — knowledge / CKO scaffold (**skeleton**)
- **Agents:** `mandala-agent-pack/` + `.cursor/agents/` — corpus + six operational agents
- **Unity / Unreal:** skeleton hosts until Play-in-Editor verified

Recent hardening (evidence-bound, not marketing): CSR governance-trace conformance check; Amendment VII/VIII opt-in gates; governed-render + external-PBR Cycles path; photoreal promote/certify CLIs restored with honest `certified: false`; SX legacy-efficient lane; ChatGPT/Jarvis tool wiring; AIKI scaffold.

## Scripts

| Command | Description |
|---------|-------------|
| `npm test` | Full smoke test suite |
| `npm run test:all` | Smoke + governance + conformance |
| `npm run test:conformance` | 17-check browser conformance profile (incl. CSR governance-trace) |
| `npm run test:governance` | Governance unit tests (`engine/governance/test/`) |
| `npm run test:runtime-provenance` | ProvenanceRecorder + ReplayService unit tests |
| `npm run test:cql` | CQL parser + interpreter |
| `npm run test:ckl` | Mythar Ascension CKL policies |
| `npm run check:types` | Package `type` consistency (`vendor/` ignored) |
| `npm run genblaze:media` | Local Genblaze FastAPI on `:8787` |
| `npm run init:cssv` | Initialize empty ledger files |
| `npm run serve` | Static browser host only |
| `npm run cssv:server` | CSSV dashboard + API only |
| `npm start` | Both servers |
| `npm run examples:gallery` | Generate gallery PNGs (needs native `canvas`; see mrs README) |
| `npm run examples:bench` | Measure local Node CanvasRenderer timings |
| `npm run test:examples` | Examples suite smoke |
| `node mandala-agent-pack/lint/run-lint.js` | Constitutional linter (**partial** heuristics) |
| `node mandala-agent-pack/drift-radar/generate-report.js` | Drift radar report |
| `node mandala-agent-pack/auto-fix/auto-fix.js` | Auto-fix **dry-run** |

Genblaze pytest (from app dir): `cd mrs/apps/genblaze-media && pytest -q`

## 4. TypeScript Runtime Integration

### MandalaEnvironmentPipeline Class
Handles buffer allocation, texture binding, and multi-pass dispatches.

- Provenance, Replay, Binding, Timeline, Evidence, CKL, CSR governance-trace (**17** checks)

Browser: **verified** via `npm run test:conformance` (Node harness uses a stub `fetch` so CKL policy load works without `file://` fetch failures).  
Runtime provenance/replay: **verified** via `npm run test:runtime-provenance` (frame hash fields + replay lineage receipts).  
Unity / Unreal: adapters **skeleton** — not claimed as 17/17 host conformance.

### Render Pass Execution Order
```
1. Instanced Grass Pass: draw(5, instanceCount) - procedural blade generation
2. Animal Shell Fur Loop: for i in 0..totalShells { drawIndexed(); } - normal extrusion + alpha-clipping
```

## 5. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Mandala RT4D Engine Loop                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  [ WebGPU Storage Buffer ] ──►  Grass Instancing (passEncoder.draw(5))   │
│                                  │                                      │
│  [ Heightmap Texture ] ──────────┼─► Terrain Height Sampling            │
│                                  │                                      │
│  [ Shell Uniform Loop ] ─────────┼─► Animal Fur Multi-Pass Extrusion      │
│                                  │                                      │
│                                  ▼                                      │
│                     [ Rigged Deform & DQS Pass ]                        │
│                                  │                                      │
│                                  ▼                                      │
│                     [ SSS & Dual-Lobe PBR Shader ]                      │
│                                  │                                      │
│                                  ▼                                      │
│                     [ SSAO Crease Occlusion Pass ]                      │
│                                  │                                      │
│                                  ▼                                      │
│                     [ TAA & Temporal Motion Vectors ]                   │
│                                  │                                      │
│                                  ▼                                      │
│                     [ Lens Polish (Bokeh & Vignette) ]                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Design Discipline: `smooth_k = 0.12`
This constant appears across three subsystems, maintaining consistent behavioral semantics:

1. **opSmoothUnion** in `sdf4d.wgsl` - sharp anatomical creases, continuous manifold
2. **GpuProfiler.resolutionAlpha** - exponential moving average smoothing factor  
3. **Skin BRDF micro-detail** - controls perturbation sharpness vs. continuity

The value `0.12` was deliberately chosen to balance sharpness with mathematical continuity across all three subsystems.

## Performance Considerations

### Grass
- **Instancing**: Single `draw(5, instanceCount)` draws millions of blades
- **Wind**: Procedural shader computation, no CPU buffer updates
- **LOD**: Fade to ground texture in distance

### Animal Fur
- **Shell Count**: Typical `total_shells = 16` gives good density without GPU overload
- **Alpha Clipping**: Reduces fragment shading cost by cutting non-strand pixels
- **Normal Extrusion**: Reuses existing DQS skeleton, no additional vertex buffers

### Shared
- **Profiler**: `GpuProfiler` with `smooth_k = 0.12` EMA tracks all pass timings
- **TAA**: Required for alpha-clipped foliage stippling
- **Lens Effects**: Bokeh + vignette post-TAA preserves strand clarity

## Integration Checklist

Full artifact index: `constitution/CHARTER.md` § Evidence map.  
Agent lawbook: [`AGENTS.md`](AGENTS.md).  
CECP / six agents: [`docs/governance/cecp/MANDALA_SIX_AGENTS.md`](docs/governance/cecp/MANDALA_SIX_AGENTS.md).  
Current media standings: [`docs/governance/cecp/trails/full-status-media-2026-07-30/`](docs/governance/cecp/trails/full-status-media-2026-07-30/).  
Quality progress log: [`docs/4d-engine/QUALITY_PROGRESS_LOG.md`](docs/4d-engine/QUALITY_PROGRESS_LOG.md).  
Photoreal strategy: [`docs/4d-engine/PHOTOREAL_PROVIDER_STRATEGY.md`](docs/4d-engine/PHOTOREAL_PROVIDER_STRATEGY.md).  
Genblaze operators + BYOK: [`docs/genblaze/`](docs/genblaze/).  
AIKI scaffold: [`aiki/README.md`](aiki/README.md).  
Maturity scorecards: [`docs/scorecards/`](docs/scorecards/).
