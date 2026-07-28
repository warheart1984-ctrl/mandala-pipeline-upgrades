/**
 * ProjectionKernel — ProjCC evaluation surface over Projector4D SoT.
 * Status: partial.
 */

import { Projector4D } from "../output/projector.js";
import { createProjectionState, toProjectorOptions } from "./ProjectionState.js";
import {
  evaluateContinuousP,
  projectPointContinuous,
  classic4Dto3D,
} from "./continuityMath.js";

export class ProjectionKernel {
  /**
   * @param {import("./ProjectionState.js").ProjectionStateInit} [initial]
   */
  constructor(initial = {}) {
    this._state = createProjectionState(initial);
  }

  /** @returns {ReturnType<typeof createProjectionState>} */
  get state() {
    return this._state;
  }

  /**
   * @param {import("./ProjectionState.js").ProjectionStateInit} patch
   */
  setState(patch) {
    this._state = createProjectionState({ ...this._state, ...patch });
    return this._state;
  }

  /**
   * @param {number} theta
   * @param {number} phi
   * @param {number} tau
   * @param {number} kappa
   * @param {import("./ProjectionState.js").ProjectionStateInit} [base]
   */
  evaluateP(theta, phi, tau, kappa, base = {}) {
    this._state = evaluateContinuousP(theta, phi, tau, kappa, {
      ...toProjectorOptions(this._state),
      modeId: this._state.modeId,
      intentId: this._state.intentId,
      ...base,
    });
    return this._state;
  }

  /**
   * @param {{x:number,y:number,z:number,w:number}} point
   */
  project(point) {
    return projectPointContinuous(point, this._state);
  }

  /** Backing classic projector for fidelity comparisons. */
  createProjector4D() {
    return new Projector4D(toProjectorOptions(this._state));
  }

  /**
   * Identity-check helper: classic closed form at zero continuous params.
   * @param {{x:number,y:number,z:number,w:number}} point
   */
  classicProject3D(point) {
    return classic4Dto3D(point, this._state.d4);
  }
}

export { createProjectionState, toProjectorOptions, evaluateContinuousP, projectPointContinuous };
