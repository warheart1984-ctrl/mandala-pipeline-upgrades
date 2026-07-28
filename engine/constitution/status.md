# Constitutional Engine — Subsystem Status

> **Authority:** Machine-readable SoT is `charter.js`. This file provides a
> human-readable summary. Does not amend `charter.js`, `charter.test.js`, or
> `AGENTS.md`.
>
> **Evidence:** 62 GPU unit tests in `mrs/packages/renderer-core/test/gpu/gpu-core.test.js`
> covering all 11 GPU modules. All WebGPU usage flags validated. No shell injection,
> no empty catches, no deterministic violations found in GPU paths.

| Subsystem | Status | Evidence |
|-----------|--------|----------|
| GPU Assist Layer | **VERIFIED** | 11/11 GPU modules covered by unit tests; all `GPUTextureUsage`/`GPUBufferUsage` flags validated; `storeOp`/`loadOp` correctness verified; no shell injection or empty catches in GPU encoders |
| CKL | **ENFORCED** | Precedent drift filter fixed (`=== false || "deny"`); `loadDefault()` resolves from `import.meta.url`; `evalModifier()` returns `env.self ?? 1`; 163+ governance tests pass |
| RT4D Print | **SOVEREIGN** | CPU RT4D remains authoritative for Digital Printer; GPU paths are assist-only; determinism boundaries enforced |
| BYOK | **LOCAL-ONLY** | BYOK keys are sessionStorage-only; never logged, persisted, or transmitted; no cloud fallback without explicit user approval |
| ProvenanceRecorder | **PARTIAL** | 14 unit tests exist; replay attach + evidence propagation verified |
| ReplayService | **PARTIAL** | 10 unit tests exist; deterministic parameter restoration verified |
| ConformanceChecker | **PARTIAL** | 17 unit tests exist; 16/16 conformance checks profiled |

## Verification history

- **GPU layer (2026-07):** Comprehensive rescan found and fixed 2 critical WebGPU bugs
  (`GPUBufferUsage.COPY_DST` → `GPUTextureUsage.COPY_DST`, `storeOp: "multisample"` →
  `storeOp: "store"`), 2 governance organ status drifts, 1 browser-safety bug (lazy
  `import()` for `fs`), 1 CKL `evalModifier()` edge case, 1 stray `console.log`.
  All 62 new GPU unit tests pass.

- **Governance layer (2026-07):** Precedent drift filter unified; charter version
  drift corrected (`"1.1.0"` → `"1.0.0"`); 3 ESM/require fixes applied; 3 test
  gap files added (ProvenanceRecorder, ReplayService, ConformanceChecker) adding
  41 tests. 204+ governance tests pass.
