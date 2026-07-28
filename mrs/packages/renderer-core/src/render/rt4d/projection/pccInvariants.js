/**
 * ProjCC invariants — catalog + predicates.
 * Status: partial for tested predicates; none are runtime-enforced (Drive-G-1).
 */

import { PHYSICAL_INVARIANT_TOL } from "../math/physicalInvariants.js";
import { Projector4D } from "../output/projector.js";
import { createProjectionState } from "./ProjectionState.js";
import { projectPointContinuous, classic4Dto3D } from "./continuityMath.js";

/** @typedef {"enforced"|"partial"|"declared"|"skeleton"|"tested"} InvariantStatus */

/**
 * @type {readonly object[]}
 */
export const PCC_INVARIANTS = Object.freeze([
  Object.freeze({
    id: "PCC-FIDELITY-ZERO",
    title: "Zero-param fidelity to Projector4D",
    statement:
      "When θ=φ=τ=κ=0, continuous projection 4D→3D matches Projector4D / classic d4/(d4+w).",
    status: /** @type {InvariantStatus} */ ("partial"),
    evidence: Object.freeze([
      "projection/continuityMath.js",
      "output/projector.js",
      "test/projection.invariants.test.js",
    ]),
    notEnforcedBecause: "Unit predicate only; no CKL gate on live renders.",
  }),
  Object.freeze({
    id: "PCC-CONTINUITY-LIPSCHITZ",
    title: "Local continuity in observation parameters",
    statement:
      "Away from d4+w_eff=0, small Δ(θ,φ,τ,κ) produce bounded Δ in screen coordinates.",
    status: /** @type {InvariantStatus} */ ("partial"),
    evidence: Object.freeze(["test/projection.continuity.test.js"]),
    notEnforcedBecause: "Finite-difference unit tests only.",
  }),
  Object.freeze({
    id: "PCC-KAPPA-IDENTITY",
    title: "κ=0 identity",
    statement: "κ=0 must not alter d4 effective scale (d4WithKappa(d4,0)===d4).",
    status: /** @type {InvariantStatus} */ ("partial"),
    evidence: Object.freeze(["projection/continuityMath.js"]),
    notEnforcedBecause: "Unit predicate only.",
  }),
  Object.freeze({
    id: "PCC-APERTURE-NE-PRINT",
    title: "Aperture ≠ print SoT",
    statement:
      "ApertureFrame3D / ProjCC aperture APIs must not replace CPU RT4D print sovereignty.",
    status: /** @type {InvariantStatus} */ ("declared"),
    evidence: Object.freeze([
      "docs/4d-engine/projection/PROJECTION_CONTINUITY_CONTRACT.md",
      "projection/ApertureFrame3D.js",
    ]),
    notEnforcedBecause: "Documentary / boundary invariant; no runtime ban yet.",
  }),
]);

/**
 * @param {{x:number,y:number,z:number,w:number}} point
 * @param {import("./ProjectionState.js").ProjectionStateInit} [opts]
 * @param {number} [tol]
 */
export function pccFidelityZeroHolds(point, opts = {}, tol = PHYSICAL_INVARIANT_TOL) {
  const state = createProjectionState({
    ...opts,
    theta: 0,
    phi: 0,
    tau: 0,
    kappa: 0,
  });
  const continuous = projectPointContinuous(point, state);
  const classic = classic4Dto3D(point, state.d4);
  const projector = new Projector4D({
    d4: state.d4,
    d3: state.d3,
    scale: state.scale,
    width: state.width,
    height: state.height,
  });
  const actual = projector.project4Dto3D(point);
  const okCont =
    Math.abs(continuous.p3.x - classic.x) < tol &&
    Math.abs(continuous.p3.y - classic.y) < tol &&
    Math.abs(continuous.p3.z - classic.z) < tol;
  const okProj =
    Math.abs(actual.x - classic.x) < tol &&
    Math.abs(actual.y - classic.y) < tol &&
    Math.abs(actual.z - classic.z) < tol;
  return { ok: okCont && okProj, continuous: continuous.p3, classic, projector3d: { x: actual.x, y: actual.y, z: actual.z } };
}

/**
 * Finite-difference continuity probe.
 * @param {{x:number,y:number,z:number,w:number}} point
 * @param {object} [opts]
 */
export function pccContinuityHolds(point, opts = {}) {
  const eps = opts.eps ?? 1e-4;
  const bound = opts.bound ?? 50; // screen px per unit param (loose local Lipschitz)
  const base = createProjectionState({
    theta: opts.theta ?? 0.2,
    phi: opts.phi ?? 0.3,
    tau: opts.tau ?? 0.1,
    kappa: opts.kappa ?? 0.05,
    d4: opts.d4 ?? 4,
    d3: opts.d3 ?? 4,
    scale: opts.scale ?? 80,
    width: opts.width ?? 640,
    height: opts.height ?? 480,
  });
  const a = projectPointContinuous(point, base).screen;
  const dims = ["theta", "phi", "tau", "kappa"];
  /** @type {object[]} */
  const steps = [];
  for (const dim of dims) {
    const patched = createProjectionState({ ...base, [dim]: base[dim] + eps });
    const b = projectPointContinuous(point, patched).screen;
    const dist = Math.hypot(b.sx - a.sx, b.sy - a.sy);
    const lip = dist / eps;
    steps.push({ dim, dist, lip, ok: lip <= bound });
  }
  return { ok: steps.every((s) => s.ok), steps, bound, eps };
}

export function listPccInvariants() {
  return PCC_INVARIANTS.map((i) => ({ id: i.id, status: i.status, title: i.title }));
}
