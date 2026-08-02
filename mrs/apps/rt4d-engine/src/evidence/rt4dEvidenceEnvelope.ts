// @mrs/rt4d-engine evidence envelope — status: declared (CIEMS-aligned, substrate-level)
//
// This module produces a CIEMS-aligned evidence envelope for each RT4D dimensional
// preview render. It is a SUBSTRATE-LEVEL artifact: the canonical consumer is the
// external CIEMS / Constitutional Runtime (JCR) on Drive-G
// (G:\CIEMS, G:\.codex\cse\constitutional-runtime). This repo does NOT host that
// runtime and does not label itself JCR/CIEMS; it declares an evidence shape that
// those higher layers are designed to ingest.
//
// The verification layer below reuses renderer-core's invariant conformance suite
// (createEvidenceRecord / validateEvidenceRecord / runInvariantConformanceSuite) as
// the substrate-level verification step; promotion into CIEMS is a separate,
// explicitly-mandated operation, not claimed here.
import {
  canonicalRt4dJson,
  sha256Hex,
  createEvidenceRecord,
  validateEvidenceRecord,
  runInvariantConformanceSuite,
} from "@mrs/renderer-core/rt4d";
import type { SceneSpec, RenderReceipt } from "../store.js";

export type Rt4dEvidenceEnvelope = {
  operation: "rt4d_dimensional_preview";
  source: "mrs-renderer-core/rt4d";
  engineVersion: "1.0.0";
  intentId: string;
  timelineId: string;
  worldId: string;
  sceneId: string;
  sceneSpecHash: string;
  sceneSha256: string;
  runId: string;
  renderKey: string;
  seed: number;
  pngSha256: string;
  parameters: Record<string, unknown>;
  parametersHash: string;
  at: string;
  replayToken: string;
};

export type SceneProvenanceIds = {
  intentId: string;
  timelineId: string;
  worldId: string;
};

/**
 * Build the CIEMS-aligned evidence envelope for an RT4D dimensional preview render.
 *
 * Fields (per AGENTS.md V "Evidence Requirements"):
 *   runId, seed, sceneSpecHash, renderKey, pngSha256, source, engineVersion, at.
 *
 * - sceneSpecHash  = sha256Hex(sceneSpec) (canonical, key-sorted)
 * - seed           = deterministic seed used for the render (replays identically)
 * - renderKey      = the engine's content-addressable render identifier
 * - pngSha256      = sha256 of the rendered PNG bytes
 * - replayToken    = sha256(sceneSpecHash + seed + parametersHash) — the single value a
 *                    future CIEMS replay gate compares to authorize a re-render as
 *                    equivalent to a prior one.
 */
export function createRt4dEvidenceEnvelope(
  scene: {
    sceneId: string;
    spec: SceneSpec;
    provenance: { hashes: { sceneSha256: string }; intentId: string; timelineId: string; worldId: string };
  },
  receipt: RenderReceipt,
  params: RenderParamsForEvidence = {},
): Rt4dEvidenceEnvelope {
  const sceneSpecHash = sha256Hex(scene.spec);
  const parameters = {
    seed: Number(receipt.renderParameters.seed),
    maxDepth: receipt.renderParameters.maxDepth,
    samplesPerPixel: receipt.renderParameters.samplesPerPixel,
    width: receipt.renderParameters.width,
    height: receipt.renderParameters.height,
    timeSeconds: receipt.renderParameters.timeSeconds ?? 0,
  };
  const parametersHash = sha256Hex(parameters);
  const replayToken = sha256Hex(
    `${sceneSpecHash}:${Number(receipt.renderParameters.seed)}:${parametersHash}`,
  );

  return {
    operation: "rt4d_dimensional_preview",
    source: "mrs-renderer-core/rt4d",
    engineVersion: "1.0.0",
    intentId: scene.provenance.intentId,
    timelineId: scene.provenance.timelineId,
    worldId: scene.provenance.worldId,
    sceneId: scene.sceneId,
    sceneSpecHash,
    sceneSha256: scene.provenance.hashes.sceneSha256,
    runId: receipt.runId,
    renderKey: receipt.renderKey ?? "",
    seed: Number(receipt.renderParameters.seed),
    pngSha256: receipt.sha256,
    parameters,
    parametersHash,
    at: receipt.at,
    replayToken,
  };
}

export type RenderParamsForEvidence = {
    seed?: number;
    maxDepth?: number;
    samplesPerPixel?: number;
    width?: number;
    height?: number;
    timeSeconds?: number;
  } | Record<string, unknown>;

/**
 * Substrate-level verification that the evidence envelope is backed by the
 * renderer-core invariant conformance suite (runInvariantConformanceSuite) and
 * that the conformance produces a passing EvidenceRecord anchored to this render.
 *
 * This module treats renderer-core's invariants as the local verification layer —
 * NOT as JCR/CIEMS itself. A future CIEMS host consumes the envelope + evidence
 * record as inputs; it is not emulated here.
 */
export function verifyRt4dEvidenceEnvelope(envelope: Rt4dEvidenceEnvelope): { ok: boolean; report: unknown } {
  const conformance: {
    records: Array<{ invariantId: string; verdict: string }>;
    summary: Record<string, number>;
    allFoundationalPassed: boolean;
  } = runInvariantConformanceSuite({ id: "rt4d-dimension-render" });
  const recordsValid = conformance.records.every((r) => validateEvidenceRecord(r).ok);
  const geoLength = conformance.records.find((r) => r.invariantId === "PI-GEO-LENGTH");
  const verdict = geoLength ? geoLength.verdict : "unevaluated";

  const evidenceRecord = createEvidenceRecord({
    invariantId: "PI-GEO-LENGTH",
    layer: "foundational",
    catalogStatus: "tested",
    predicateResult: { ok: verdict === "pass" },
    measurementIds: ["PI-GEO-LENGTH"],
    evidenceAnchors: [envelope.sceneSpecHash, envelope.renderKey, envelope.pngSha256],
    runtimeId: envelope.source,
    note:
      "Substrate-level anchor: this render's determinism (seed-driven mulberry32 rng, no " +
      "Math.random in the path) is claimed under PI-GEO-LENGTH (4D length preservation) via " +
      "the renderer-core conformance suite. Does not assert CIEMS/JCR enforcement.",
  });

  return {
    ok: Boolean(conformance.allFoundationalPassed) && recordsValid && verdict === "pass",
    report: {
      envelope,
      recordsValid,
      conformancesummary: conformance.summary,
      allFoundationalPassed: conformance.allFoundationalPassed,
      evidenceRecord,
    },
  };
}
