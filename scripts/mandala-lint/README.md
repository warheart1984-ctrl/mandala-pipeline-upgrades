# Mandala Constitutional Linter

> **Status:** **partial** — heuristic / substring probes against **real** repo paths.
> Does **not** claim full constitutional enforcement (Drive-G-1).

## Run

```bash
node scripts/mandala-lint/run.mjs
node scripts/mandala-lint/run.mjs --json
```

Exit code `1` when any issue has severity `error`. `skip` / `warn` alone do not fail.

## What it checks (honest)

| Check | Real path(s) | Fidelity |
|-------|----------------|----------|
| Charter version / organ status | `engine/constitution/charter.js` | partial |
| CKL denial filter / loadDefault | `engine/governance/ConstitutionalKnowledgeLayer.js` | partial |
| Determinism contracts | `sovereign-x/router/contracts/gpuPrintSafeguard.js` (+ related) | partial |
| GPU assist-only | `gpuPrintSafeguard` (not “print” substrings in GPU files) | partial |
| BYOK | `mrs/apps/genblaze-media/app/static/index.html` + `byok.py` | partial |
| Printer / evidence secrets | storyforge-boundary printer + SX lineage (skip if missing) | partial |
| ESM / WebGPU C1–C2 | real `TimelineSerializer` / encode / EnvironmentMapper / GPUMeshRenderer | partial |
| NVENC shell | prefers `execFile` patterns; does not gut encoders | partial |

## Intentionally not done

- Fictional `genblaze/src/lib/nimClient.js` or `engine/printer/DigitalPrinter.js`
- Auto-mutating charter / CKL / policies
- Treating PASS as “enforced”

Related: `mandala-agent/drift-radar/`, `mandala-agent/auto-fix/` (dry-run default).
