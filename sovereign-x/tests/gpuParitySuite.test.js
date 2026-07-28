/**
 * Vendor-neutral GPU parity suite — SKELETON only.
 *
 * Drive-G-1: Does NOT claim enforced CPU↔GPU print parity.
 * SSIM/MSE cases are skipped until real plates + backends exist.
 * Stub computeMetrics returning 1.0/0.0 must never be treated as PASS evidence.
 */

import assert from "node:assert/strict";
import { describe, it } from "node:test";
import {
  loadGpuSkillsRegistry,
  route,
} from "../router/index.js";

/**
 * Stub metrics — labeled skeleton. Do not use as live parity proof.
 * @returns {{ ssim: number, mse: number, status: string }}
 */
function computeMetrics(_a, _b) {
  return { ssim: 1.0, mse: 0.0, status: "skeleton" };
}

describe("Vendor-neutral GPU parity suite (skeleton)", () => {
  it("registry lists GPU assist skills + authoritative print", () => {
    const reg = loadGpuSkillsRegistry({ reload: true });
    assert.equal(reg.authoritativePrint, "cpu.rt4d.print");
    assert.ok(reg.skills["gpu.gen.nvidia.nim_flux"]);
    assert.ok(reg.skills["gpu.compute.amd.hip"]);
  });

  it("computeMetrics stub is explicitly skeleton-labeled", () => {
    const m = computeMetrics({}, {});
    assert.equal(m.status, "skeleton");
    assert.equal(m.ssim, 1.0);
    assert.equal(m.mse, 0.0);
  });

  it(
    "CPU vs NVIDIA SSIM/MSE within thresholds",
    { skip: "skeleton: no live GPU plates / parity receipts yet" },
    async () => {
      const scene = { intentId: "test-1", modality: "scene" };
      const cpuPlate = await route("cpu.rt4d.print", scene);
      const nvidiaPlate = await route("gpu.compute.nvidia.cuda", {
        ...scene,
        mode: "parity",
      });
      const metrics = computeMetrics(cpuPlate, nvidiaPlate);
      assert.ok(metrics.ssim >= 0.98);
      assert.ok(metrics.mse <= 0.002);
    },
  );

  it(
    "CPU vs AMD SSIM/MSE within thresholds",
    { skip: "skeleton: no live GPU plates / parity receipts yet" },
    async () => {
      const scene = { intentId: "test-2", modality: "scene" };
      const cpuPlate = await route("cpu.rt4d.print", scene);
      const amdPlate = await route("gpu.compute.amd.hip", {
        ...scene,
        mode: "parity",
      });
      const metrics = computeMetrics(cpuPlate, amdPlate);
      assert.ok(metrics.ssim >= 0.98);
      assert.ok(metrics.mse <= 0.002);
    },
  );
});
