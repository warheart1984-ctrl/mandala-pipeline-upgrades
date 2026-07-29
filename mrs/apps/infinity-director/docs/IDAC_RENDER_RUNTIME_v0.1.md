# IDAC.RenderRuntime v0.1

**Status:** **partial** — `app/idac/domains/rendering/runtime.py`

## Components

| Component | Status | Today |
|-----------|--------|-------|
| RenderExecutor | partial | `dispatch_render` |
| TileScheduler | declared | ATCM tile grid metadata only |
| ShadingEngine | declared | `execution_mode: full_frame_dispatch` |
| PostFXEngine | declared | math_strategies upscale metadata |
| EvidenceEmitter | partial | EvidenceContract builder |
| ViolationEmitter | partial | PlanViolation JSON |

## Honesty

Genblaze/Engine3D stills are **full-frame**. Tile-faithful per-tile execution is **declared** future work; conformance tests document the gap.

## Conformance hooks

Runtime meta attached under `execution_trace.runtime` for suite assertions without claiming tile dispatch.
