# Mandala RT4D Pipeline Upgrades: Organic Environments

**Start here:** [`docs/START_HERE_MRS_30_MIN.md`](docs/START_HERE_MRS_30_MIN.md) — practical onboarding in ~30 minutes (commands, layout, role paths). Not marketing.

Published title: **4D Rendering System v1.0**  
Formal engine name: **RT4D** (*Ray Tracer for Four Dimensions*)  
Official validation scene: **Hyper-Caustic Lens**

1. **Instanced Grass Geometry** - GPU-driven blade rendering with wind simulation
2. **Animal Shell Fur** - DQS normal extrusion with alpha-noise hair strands
3. **Terrain Heightmap Integration** - Ground plane snapshots for both systems

## Key Files Modified/Created

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

```bash
cd mrs && pnpm run setup   # fresh clone: install + rebuild canvas/esbuild
```

### Windows native canvas (optional for widget)

Headless PNG (CLI, gallery, some exports) needs native `canvas` + VS C++ Build Tools on Windows — see [`mrs/README.md`](mrs/README.md#windows-native-canvas-honest). Browser demo and ChatGPT widget use Canvas2D and do **not** require cairo.

## Capability snapshot

Statuses below match charter evidence (not marketing). Details: [`constitution/CHARTER.md`](constitution/CHARTER.md).

| Capability | Status |
| --- | --- |
| 4D parametric surfaces | Present |
| RT4D path rendering | Present |
| Browser host | Present |
| CSSV ledger | Partial |
| Hyper-Caustic Lens validation | Present |
| WebGPU | Present |
| Canvas fallback | Present |
| Unity adapter | Partial |
| Unreal adapter | Partial |
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
| Unity FourDAdapter (Scene3D+lineage) | Skeleton |
| Unreal FourDAdapter (Scene3D+lineage) | Skeleton (`unreal/FourDAdapter/`) |
| FourDRenderer v2.0 architecture / RFCs | Declared / draft (`docs/4d-engine/v2/`) — Phase 1 **docs**; GPU/RHI **roadmap** |
| FourDRenderer v2 Unreal RHI / Nanite / Lumen | Roadmap (not FourDAdapter v1.1) |
| RT4D GPU evolution (v2–v4) | Roadmap / declared (`docs/4d-engine/rt4d/`) — wavefront, denoise, multi-GPU, Vulkan/DX **not implemented** |
| Object storage (B2 S3-compatible) | Declared / operator-configured (`@mrs/storage-b2`, [`docs/ops/BACKBLAZE_B2_S3.md`](docs/ops/BACKBLAZE_B2_S3.md)) — not cloud rendering complete |

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

### Fur Noise Formula
```wgsl
fn fur_strand_noise(p: vec3<f32>, scale: f32) -> f32 {
    let q = p * scale;
    return fract(sin(dot(q, vec3<f32>(12.9898, 78.233, 45.543))) * 43758.5453);
}
```

## 3. Terrain Heightmap Integration

### Heightmap Pipeline
1. Load bitmap via `device.queue.copyExternalImageToTexture()`
2. Create `r32float` texture: `[width, height, 1]`
3. Sample in shader: `textureSampleLevel(terrain_heightmap, height_sampler, terrain_uv, 0.0).r`
4. Scale to elevation: `height_sample * 20.0`

| Command | Description |
|---------|-------------|
| `npm test` | Full smoke test suite |
| `npm run test:conformance` | 16-check browser conformance profile |
| `npm run test:cql` | CQL parser + interpreter |
| `npm run test:ckl` | Mythar Ascension CKL policies |
| `npm run init:cssv` | Initialize empty ledger files |
| `npm run serve` | Static browser host only |
| `npm run cssv:server` | CSSV dashboard + API only |
| `npm start` | Both servers |
| `npm run examples:gallery` | Generate gallery PNGs (needs native `canvas`; see mrs README) |
| `npm run examples:bench` | Measure local Node CanvasRenderer timings |
| `npm run test:examples` | Examples suite smoke |

## 4. TypeScript Runtime Integration

### MandalaEnvironmentPipeline Class
Handles buffer allocation, texture binding, and multi-pass dispatches.

**Key Methods:**
- `initGrassSystem(instances, heightmapBitmap)` - Allocates storage buffer + loads heightmap
- `initShellFurSystem()` - Creates 16-byte shell uniform buffer
- `recordRenderPass(...)` - Executes grass draw + shell fur multi-pass loop

### GrassInstance Interface
```typescript
export interface GrassInstance {
  position_xz: [number, number];
  scale: number;
  rotation: number;
}
```

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

- [ ] Add `MorphCorrective.wgsl` splice into `RiggedDeform.vert.wgsl` before DQS skinning
- [ ] Insert `LensEffects.frag.wgsl` as full-screen quad pass after TAA
- [ ] Integrate `GpuProfiler` into `WebGPURenderer.render()` with begin/end timestamp pairs
- [ ] Add `uvCoord` to `FrameParams` in shader entry point
- [ ] Set `activeCount = 2u` (digit/face) / `4u` (body/tissue) in rig vertex shader
- [ ] Load terrain heightmap bitmap into `r32float` texture
- [ ] Populate GrassInstance storage buffer per frame
- [ ] Initialize ShellUniforms per animal mesh render
- [ ] Wire `recordRenderPass()` into main render loop
