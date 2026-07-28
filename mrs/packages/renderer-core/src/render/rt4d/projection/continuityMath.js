/**
 * Continuous P(θ, φ, τ, κ) math aligned with Projector4D closed forms.
 * Status: partial — unit-tested continuity + fidelity; not path-tracer enforced.
 */

import { vec4 } from "../math/vec4.js";
import { Projector4D } from "../output/projector.js";
import { createProjectionState, toProjectorOptions } from "./ProjectionState.js";

/**
 * Effective w after τ offset (observation slice).
 * @param {number} w
 * @param {number} tau
 */
export function effectiveW(w, tau) {
  return w - tau;
}

/**
 * Classic 4D→3D scale factor with τ-adjusted w.
 * Matches Projector4D when tau=0: d4/(d4+w).
 * @param {number} d4
 * @param {number} w
 * @param {number} [tau]
 */
export function wProjFactor(d4, w, tau = 0) {
  return d4 / (d4 + effectiveW(w, tau));
}

/**
 * Apply SO(2)×elevation view rotation after 4D→3D (θ polar, φ azimuth).
 * Identity when θ=0, φ=0: returns (x,y,z) unchanged.
 * @param {{x:number,y:number,z:number}} p3
 * @param {number} theta
 * @param {number} phi
 */
export function applyViewOrientation(p3, theta, phi) {
  const ct = Math.cos(theta);
  const st = Math.sin(theta);
  const cp = Math.cos(phi);
  const sp = Math.sin(phi);
  // Rotate: first around Z by φ, then tilt by θ in the XZ plane.
  const x1 = p3.x * cp - p3.y * sp;
  const y1 = p3.x * sp + p3.y * cp;
  const z1 = p3.z;
  const x2 = x1 * ct + z1 * st;
  const y2 = y1;
  const z2 = -x1 * st + z1 * ct;
  return { x: x2, y: y2, z: z2 };
}

/**
 * Declared κ modulation of d4 (identity at κ=0). Soft caustic aperture weight.
 * Does not invent a new print formula — scale factor only.
 * @param {number} d4
 * @param {number} kappa
 */
export function d4WithKappa(d4, kappa) {
  // κ=0 → classic; small positive κ gently increases focal distance (declared).
  return d4 * (1 + 0.1 * kappa);
}

/**
 * Evaluate continuous projection map → ProjectionState.
 * @param {number} theta
 * @param {number} phi
 * @param {number} tau
 * @param {number} kappa
 * @param {import("./ProjectionState.js").ProjectionStateInit} [base]
 */
export function evaluateContinuousP(theta, phi, tau, kappa, base = {}) {
  return createProjectionState({
    ...base,
    theta,
    phi,
    tau,
    kappa,
    d4: base.d4 ?? 4,
    d3: base.d3 ?? 4,
    status: "partial",
  });
}

/**
 * Project a 4D point through P(θ,φ,τ,κ) using Projector4D fidelity at κ=τ=θ=φ=0.
 *
 * @param {{x:number,y:number,z:number,w:number}} point
 * @param {ReturnType<typeof createProjectionState>} state
 * @returns {{ p3: {x:number,y:number,z:number}, screen: {sx:number,sy:number}, wFactor: number }}
 */
export function projectPointContinuous(point, state) {
  const d4 = d4WithKappa(state.d4, state.kappa);
  const wFactor = wProjFactor(d4, point.w, state.tau);
  const raw3 = {
    x: point.x * wFactor,
    y: point.y * wFactor,
    z: point.z * wFactor,
  };
  const oriented = applyViewOrientation(raw3, state.theta, state.phi);
  const projector = new Projector4D({
    ...toProjectorOptions(state),
    d4,
  });
  // Feed oriented 3D through the same 3D→2D closed form as Projector4D.
  const screen = projector.project3Dto2D(vec4(oriented.x, oriented.y, oriented.z, 0));
  return { p3: oriented, screen, wFactor };
}

/**
 * Closed-form expected 4D→3D when θ=φ=τ=κ=0 (must match Projector4D).
 * @param {{x:number,y:number,z:number,w:number}} point
 * @param {number} d4
 */
export function classic4Dto3D(point, d4) {
  const f = d4 / (d4 + point.w);
  return { x: point.x * f, y: point.y * f, z: point.z * f };
}
