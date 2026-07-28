# 03 — Implementor notes

**Trail:** `printer-gpu-quality-speed-2026-07`  
**Stage:** Implementor  
**Status:** **declared** — **no implementation this pass** (brainstorming hard-gate + parent order)

## What was done

- Design + plan + trail authored only
- Parallel domain explores (A printer CPU, B Genblaze NVIDIA, C RT4D GPU, D AMD) dispatched for evidence

## Deferred code (do not claim shipped)

| Deferred work | Why deferred |
|---------------|--------------|
| `backend` selector on print pipeline | Needs design approval + parity tests |
| Wire `GpuPathTracer4D` into printer execute | Node WebGPU absent; parity unknown |
| Quality-per-sample metric exporter | Plan task; not started |
| CUDA / HIP backends | **absent** in repo |
| NIM beauty SoT | Rejected by ADR |

## Regressions preserved

- v2.0 profiles, denoise, soft penumbra, sovereignty — untouched

## Handoff

Reviewer: check design vs BOUNDARY + AGENTS + Drive-G-1 tags.
