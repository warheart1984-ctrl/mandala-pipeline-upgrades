/**
 * Path-tracer integration hooks for ProjCC.
 * Status: declared — not fully wired into PathTracer4D execute path.
 */

import { createProjectionState } from "./ProjectionState.js";
import { ProjectionKernel } from "./ProjectionKernel.js";
import { createApertureFrame3D } from "./ApertureFrame3D.js";
import { resolveObservationPreset } from "./ObservationModePresets.js";

export const PATH_TRACER_PROJECTION_HOOK_STATUS = /** @type {const} */ ("declared");

/**
 * Build a declared observation bundle for a future PathTracer4D bind site.
 * Does not mutate the integrator.
 *
 * @param {{
 *   modeId?: string,
 *   width?: number,
 *   height?: number,
 *   intentId?: string|null,
 *   theta?: number,
 *   phi?: number,
 *   tau?: number,
 *   kappa?: number,
 * }} [opts]
 */
export function createPathTracerProjectionHooks(opts = {}) {
  const modeId = opts.modeId ?? "perspective_w";
  let resolved;
  try {
    resolved = resolveObservationPreset(modeId, {
      width: opts.width,
      height: opts.height,
      intentId: opts.intentId ?? null,
      theta: opts.theta,
      phi: opts.phi,
      tau: opts.tau,
      kappa: opts.kappa,
    });
  } catch {
    resolved = {
      state: createProjectionState({
        modeId,
        width: opts.width,
        height: opts.height,
        intentId: opts.intentId ?? null,
        status: "declared",
      }),
      observationModeId: null,
      projectionPolicyId: null,
      preset: null,
    };
  }

  const kernel = new ProjectionKernel(resolved.state);
  const aperture = createApertureFrame3D(resolved.state, {
    x: 0,
    y: 0,
    width: resolved.state.width,
    height: resolved.state.height,
  });

  return Object.freeze({
    status: PATH_TRACER_PROJECTION_HOOK_STATUS,
    wiredIntoPathTracer4D: false,
    state: resolved.state,
    kernel,
    aperture,
    observationModeId: resolved.observationModeId,
    projectionPolicyId: resolved.projectionPolicyId,
    /**
     * Declared bind site name for future integrator wiring.
     * Do not claim PathTracer4D reads this yet.
     */
    bindSite: "PathTracer4D.observationProjection (declared)",
  });
}

/**
 * @returns {{ status: string, wired: boolean, note: string }}
 */
export function describePathTracerProjectionIntegration() {
  return {
    status: PATH_TRACER_PROJECTION_HOOK_STATUS,
    wired: false,
    note:
      "Hooks package ProjectionState + ApertureFrame3D for a future PathTracer4D bind; CPU print SoT unchanged.",
  };
}
