/**
 * @mrs/sovereign-x-router — Sovereign X multi-vendor capability registration.
 *
 * STATUS: **partial** (registry load + dispatch stubs enforced in unit tests;
 * vendor runtimes not invoked; print SoT never allowed).
 */

export {
  REGISTRY_PATH,
  loadVendorCapabilityRegistry,
  getCapability,
  getForbiddenPrintCapabilityIds,
  indexCapabilitiesById,
  clearRegistryCache,
} from "./registry.js";

export {
  DISPATCH_CODES,
  dispatchVendorCapability,
  listUpstreamCapabilityIds,
  listForbiddenPrintCapabilityIds,
} from "./dispatch.js";
