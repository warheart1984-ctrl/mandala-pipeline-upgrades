/**
 * Observation mode presets for ProjCC.
 * Status: partial — preset objects + resolve tests; v2 path-routing remains declared.
 */

import { createProjectionState } from "./ProjectionState.js";
import {
  OBSERVATION_MODE_IDS,
  PROJECTION_POLICY_IDS,
  mapObservationModeChoice,
} from "../../../live-link/shadingWire.js";

/**
 * Canonical preset table (PLP mode ids + continuous defaults).
 * @type {Readonly<Record<string, object>>}
 */
export const OBSERVATION_MODE_PRESETS = Object.freeze({
  perspective_w: Object.freeze({
    modeId: "perspective_w",
    liveLinkChoice: "Perspective4DTo3D",
    theta: 0,
    phi: 0,
    tau: 0,
    kappa: 0,
    description: "Classic perspective_w — identity continuous params",
    status: "partial",
  }),
  slice_hyperplane: Object.freeze({
    modeId: "slice_hyperplane",
    liveLinkChoice: "WSliceConstant",
    theta: 0,
    phi: 0,
    tau: 0,
    kappa: 0,
    description: "W-slice / hyperplane observation; τ selects slice offset at resolve time",
    status: "partial",
  }),
  intentional_orbit: Object.freeze({
    modeId: "intentional_orbit",
    liveLinkChoice: "Perspective4DTo3D",
    theta: Math.PI / 6,
    phi: Math.PI / 4,
    tau: 0,
    kappa: 0,
    description: "Declared orbit preset — continuous view angles non-zero",
    status: "declared",
  }),
  soft_caustic: Object.freeze({
    modeId: "soft_caustic",
    liveLinkChoice: "Perspective4DTo3D",
    theta: 0,
    phi: 0,
    tau: 0,
    kappa: 0.5,
    description: "Soft κ aperture weight — declared caustic observation",
    status: "declared",
  }),
});

/**
 * @param {string} modeId
 * @param {import("./ProjectionState.js").ProjectionStateInit} [overrides]
 */
export function resolveObservationPreset(modeId, overrides = {}) {
  const preset = OBSERVATION_MODE_PRESETS[modeId];
  if (!preset) {
    throw new Error(`Unknown observation mode preset: ${modeId}`);
  }
  const live = mapObservationModeChoice(preset.liveLinkChoice);
  const state = createProjectionState({
    modeId: preset.modeId,
    theta: preset.theta,
    phi: preset.phi,
    tau: preset.tau,
    kappa: preset.kappa,
    status: preset.status === "declared" ? "declared" : "partial",
    ...overrides,
  });
  return Object.freeze({
    preset,
    state,
    observationModeId: live.observationModeId,
    projectionPolicyId: live.projectionPolicyId,
  });
}

export function listObservationPresets() {
  return Object.keys(OBSERVATION_MODE_PRESETS);
}

export { OBSERVATION_MODE_IDS, PROJECTION_POLICY_IDS };
