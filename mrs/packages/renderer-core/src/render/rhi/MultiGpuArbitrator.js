/**
 * Multi-GPU arbitration — Phase C **declared** stub (Drive-G-1).
 * Always falls back to strategy `"single"`. No device scheduling or CSSV write yet.
 *
 * Contract: docs/4d-engine/rt4d/RT4D_V4_MULTI_GPU_CONTRACT.md
 * Schema: cssv/multi-gpu/cssv-multi-gpu-schema.json
 */

/**
 * @typedef {object} MultiGpuDecision
 * @property {string} frameId
 * @property {import("./RhiTypes.js").RhiDeviceInfo[]} selectedDevices
 * @property {"single"|"split-frame"|"tiles"} strategy
 * @property {object} [hints]
 */

export class MultiGpuArbitrator {
  /**
   * @param {import("./RhiContract.js").Rhi|null} [rhi]
   */
  constructor(rhi = null) {
    this.rhi = rhi;
  }

  /**
   * Decide which devices to use for a frame.
   * Phase C: returns empty selection + `"single"` — selection logic **not implemented**.
   *
   * @param {import("./RhiContract.js").Rhi} rhi
   * @param {number} requestedCount
   * @returns {Promise<MultiGpuDecision>}
   */
  async decideDevices(rhi, requestedCount) {
    void rhi;
    void requestedCount;
    return {
      frameId: "",
      selectedDevices: [],
      strategy: "single",
    };
  }

  /**
   * Plan a frame’s device set (alias surface for future schedulers).
   *
   * @param {string} frameId
   * @param {number} requestedCount
   * @param {object} [hints]
   * @returns {Promise<MultiGpuDecision>}
   */
  async planFrame(frameId, requestedCount, hints = {}) {
    void requestedCount;
    return {
      frameId: frameId ?? "",
      selectedDevices: [],
      strategy: "single",
      hints,
    };
  }

  /**
   * Optional CSSV evidence write — Phase C **no-op**.
   * @param {MultiGpuDecision} decision
   * @returns {Promise<void>}
   */
  async recordDecision(decision) {
    void decision;
  }
}
