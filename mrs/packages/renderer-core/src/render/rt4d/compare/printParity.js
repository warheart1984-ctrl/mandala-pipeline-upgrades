/**
 * Print-oriented CPU↔GPU parity probe helpers.
 *
 * STATUS: **partial** — receipt/metrics **enforced** in unit tests;
 * live WebGPU on Node is skipped (skip ≠ pass).
 */

/**
 * Probe whether a WebGPU adapter is available in this runtime.
 * Node without Dawn/navigator.gpu → unavailable.
 *
 * GPU host note (tao-setup-nvidia-gpu-host skill, Drive-G-1):
 *   Claiming NVIDIA CUDA print acceleration also requires a checked GPU host
 *   (nvidia-smi / container toolkit). That path remains **absent** for printer.
 *   AMD ROCm/HIP remains **absent** — use rocm-doctor/rocm-setup skills only
 *   when diagnosing a future host, not as evidence of print support.
 *
 * @returns {{ available: boolean, reason: string, statusTag: string }}
 */
export function probeWebGpuAvailability() {
  const nav =
    typeof globalThis !== "undefined" ? globalThis.navigator : undefined;
  if (!nav || !nav.gpu) {
    return {
      available: false,
      reason: "navigator.gpu missing (typical Node CI) — skip ≠ pass",
      statusTag: "partial",
    };
  }
  return {
    available: true,
    reason: "navigator.gpu present — live adapter probe still required",
    statusTag: "partial",
  };
}

/**
 * Build a print-sized scene config for parity receipts (not a full GLB path).
 * Used by unit tests with synthetic RGBA plates.
 */
export function printParitySceneConfig(overrides = {}) {
  return {
    sceneId: "print-parity-tiny",
    seed: 42,
    width: 16,
    height: 16,
    spp: 8,
    glbPath: "synthetic://print-parity",
    camera: {},
    thresholds: { maxPixelDelta: 0.01, mse: 0.0001, ssim: 0.99 },
    ...overrides,
  };
}
