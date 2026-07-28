# @mrs/sovereign-x-router

Thin **Sovereign X** multi-vendor capability registry + dispatch stubs.

**Status:** **partial** — registry load and reject/allow decisions are covered by
unit tests; vendor runtimes are **not** invoked; Digital Printer beauty SoT is
never allowed.

## What this is

Machine-readable mapping of NVIDIA/AMD vendor-skill capability IDs → skill names
→ `upstream` / `forbidden_for_print` → `declared` | `partial`.

## What this is not

- Not a CUDA/HIP/ROCm print backend
- Not Digital Printer SoT (see
  [`CONTRACT_DIGITAL_PRINT.md`](../../adapters/storyforge-boundary/CONTRACT_DIGITAL_PRINT.md))
- Not a claim that AMD backends exist in-repo (AMD is **host-capability driven**)

## Usage

```js
import {
  dispatchVendorCapability,
  loadVendorCapabilityRegistry,
} from "@mrs/sovereign-x-router";

const allow = dispatchVendorCapability("ai.gen.nvidia.flux", {
  intentLane: "lookdev",
});
// allow.ok === true

const ban = dispatchVendorCapability("gpu.print.beauty", {});
// ban.ok === false, code PRINT_SOT_BANNED

const printSmuggle = dispatchVendorCapability("ai.gen.nvidia.flux", {
  asPrintSoT: true,
});
// printSmuggle.ok === false, code FORBIDDEN_FOR_PRINT
```

## Tests

```bash
npm test --prefix mrs/packages/sovereign-x-router
```

## Trail

`docs/governance/cecp/trails/sovereign-x-vendor-router-2026-07/`

## Related

- `docs/superpowers/specs/2026-07-28-vendor-skills-install-note.md`
- `docs/governance/cecp/trails/vendor-skills-fixup-2026-07/`
