/**
 * HyperCausticLensVerifier — hooks for official Hyper-Caustic Lens validation.
 * Status: declared (stubs OK). Soft-skip when reference dataset/hashes absent.
 *
 * Scene factory SoT: scene/TestHyperCausticLens.js
 * Docs: docs/4drs/validation/Hyper-Caustic-Lens.md
 */

import { createHyperCausticLens } from "../scene/TestHyperCausticLens.js";
import { createProjectionState } from "./ProjectionState.js";
import { ProjectionKernel } from "./ProjectionKernel.js";

export const HYPER_CAUSTIC_VERIFIER_STATUS = /** @type {const} */ ("declared");

/**
 * @typedef {object} LensVerifierResult
 * @property {boolean} ok
 * @property {"pass"|"soft_skip"|"fail"} verdict
 * @property {string} status
 * @property {string} reason
 * @property {object} [meta]
 */

/**
 * Probe that the validation scene factory is loadable and returns scene+camera.
 * Does not claim pixel north-star PASS.
 * @param {object} [options]
 * @returns {LensVerifierResult}
 */
export function verifyHyperCausticLensFactory(options = {}) {
  try {
    const { scene, camera } = createHyperCausticLens(options);
    const ok = Boolean(scene && camera);
    return {
      ok,
      verdict: ok ? "pass" : "fail",
      status: HYPER_CAUSTIC_VERIFIER_STATUS,
      reason: ok
        ? "createHyperCausticLens returned scene+camera (factory hook)"
        : "factory returned incomplete bundle",
      meta: {
        hasScene: Boolean(scene),
        hasCamera: Boolean(camera),
        width: camera?.width ?? null,
        height: camera?.height ?? null,
      },
    };
  } catch (err) {
    return {
      ok: false,
      verdict: "fail",
      status: HYPER_CAUSTIC_VERIFIER_STATUS,
      reason: `factory threw: ${err instanceof Error ? err.message : String(err)}`,
    };
  }
}

/**
 * North-star image compare hook.
 * Soft-skips when no reference dataset path / hashes provided.
 *
 * @param {{
 *   referenceHash?: string|null,
 *   candidateHash?: string|null,
 *   referencePath?: string|null,
 * }} [opts]
 * @returns {LensVerifierResult}
 */
export function verifyHyperCausticLensNorthStar(opts = {}) {
  const { referenceHash = null, candidateHash = null, referencePath = null } = opts;
  if (!referenceHash && !referencePath) {
    return {
      ok: true,
      verdict: "soft_skip",
      status: HYPER_CAUSTIC_VERIFIER_STATUS,
      reason:
        "No reference dataset/hash supplied — soft-skip (declared; not a visual PASS)",
      meta: { referenceHash, candidateHash, referencePath },
    };
  }
  if (referenceHash && candidateHash && referenceHash === candidateHash) {
    return {
      ok: true,
      verdict: "pass",
      status: "partial",
      reason: "candidateHash matches referenceHash",
      meta: { referenceHash, candidateHash },
    };
  }
  if (referenceHash && candidateHash && referenceHash !== candidateHash) {
    return {
      ok: false,
      verdict: "fail",
      status: "partial",
      reason: "candidateHash does not match referenceHash",
      meta: { referenceHash, candidateHash },
    };
  }
  return {
    ok: true,
    verdict: "soft_skip",
    status: HYPER_CAUSTIC_VERIFIER_STATUS,
    reason: "Reference path noted but hash compare not wired — soft-skip",
    meta: { referencePath, referenceHash, candidateHash },
  };
}

/**
 * Wire ProjCC kernel against the lens camera defaults (structural hook only).
 * @param {object} [options]
 * @returns {LensVerifierResult}
 */
export function verifyHyperCausticLensProjectionHook(options = {}) {
  const factory = verifyHyperCausticLensFactory(options);
  if (!factory.ok) return factory;
  const state = createProjectionState({
    modeId: "soft_caustic",
    kappa: 0.25,
    width: options.width ?? 640,
    height: options.height ?? 480,
    status: "declared",
  });
  const kernel = new ProjectionKernel(state);
  const probe = kernel.project({ x: 0.1, y: 0, z: 0.2, w: 0.05 });
  const finite =
    Number.isFinite(probe.screen.sx) && Number.isFinite(probe.screen.sy);
  return {
    ok: finite,
    verdict: finite ? "pass" : "fail",
    status: HYPER_CAUSTIC_VERIFIER_STATUS,
    reason: finite
      ? "ProjCC kernel projected probe point through soft_caustic state (structural)"
      : "non-finite screen sample",
    meta: { screen: probe.screen, status: state.status },
  };
}

/**
 * Run all declared verifier hooks.
 * @param {object} [opts]
 */
export function runHyperCausticLensVerifierSuite(opts = {}) {
  const results = [
    verifyHyperCausticLensFactory(opts),
    verifyHyperCausticLensProjectionHook(opts),
    verifyHyperCausticLensNorthStar(opts),
  ];
  const hardFail = results.some((r) => r.verdict === "fail");
  return {
    ok: !hardFail,
    status: HYPER_CAUSTIC_VERIFIER_STATUS,
    results,
  };
}
