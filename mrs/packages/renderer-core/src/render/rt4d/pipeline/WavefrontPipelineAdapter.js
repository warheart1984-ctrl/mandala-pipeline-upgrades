import { selectWavefrontConfig } from "./WavefrontConfigSelector.js";
import { createRt4dWavefrontPipeline } from "../gpu/wavefront/WavefrontPipeline.js";
import { prepareWorld } from "../WorldOrchestrator.js";

/**
 * Host-facing adapter beside RT4DGPURenderer (Phase B stub path).
 * Phase C: optional worldDoc / worldContext → prepareWorld + CPU wave step (skeleton).
 *
 * @param {string} worldId
 * @param {object} opts
 * @param {"baseline"|"high"|"ultra"} [opts.quality]
 * @param {"browser"|"unity"|"unreal"|"native"} [opts.host]
 * @param {boolean} [opts.multiGpuAvailable]
 * @param {object} [opts.worldDoc]
 * @param {object} [opts.worldContext]
 * @param {boolean} [opts.stepWave=true]
 * @param {(rec: object) => Promise<void>|void} [opts.onEvidence]
 */
export async function renderWavefrontFrame(worldId, opts = {}) {
  let worldContext = opts.worldContext ?? null;
  if (!worldContext && opts.worldDoc) {
    worldContext = prepareWorld(opts.worldDoc);
  }
  if (worldContext?.waveField && opts.stepWave !== false) {
    worldContext.waveField.step();
  }

  const config = selectWavefrontConfig({
    quality: opts.quality,
    host: opts.host,
    multiGpuAvailable: opts.multiGpuAvailable === true,
  });
  const pipeline = await createRt4dWavefrontPipeline("webgpu", {
    onEvidence: opts.onEvidence,
  });
  await pipeline.renderFrame(worldId, config);
  return {
    worldId,
    config,
    evidence: pipeline.evidence.records,
    dispatchLog: pipeline.rhi.dispatchLog ?? [],
    worldContext,
  };
}
