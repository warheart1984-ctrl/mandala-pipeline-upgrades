/**
 * ProjCC / intentional 4D projection continuity package.
 * Extends Projector4D SoT — does not invent a parallel print kernel.
 */

export {
  createProjectionState,
  toProjectorOptions,
} from "./ProjectionState.js";

export {
  ProjectionKernel,
  evaluateContinuousP,
  projectPointContinuous,
} from "./ProjectionKernel.js";

export {
  effectiveW,
  wProjFactor,
  applyViewOrientation,
  d4WithKappa,
  classic4Dto3D,
} from "./continuityMath.js";

export {
  PCC_INVARIANTS,
  pccFidelityZeroHolds,
  pccContinuityHolds,
  listPccInvariants,
} from "./pccInvariants.js";

export {
  OBSERVATION_MODE_PRESETS,
  resolveObservationPreset,
  listObservationPresets,
  OBSERVATION_MODE_IDS,
  PROJECTION_POLICY_IDS,
} from "./ObservationModePresets.js";

export {
  createApertureFrame3D,
  apertureSampleDirection,
} from "./ApertureFrame3D.js";

export {
  HYPER_CAUSTIC_VERIFIER_STATUS,
  verifyHyperCausticLensFactory,
  verifyHyperCausticLensNorthStar,
  verifyHyperCausticLensProjectionHook,
  runHyperCausticLensVerifierSuite,
} from "./HyperCausticLensVerifier.js";

export {
  PATH_TRACER_PROJECTION_HOOK_STATUS,
  createPathTracerProjectionHooks,
  describePathTracerProjectionIntegration,
} from "./pathTracerHooks.js";
