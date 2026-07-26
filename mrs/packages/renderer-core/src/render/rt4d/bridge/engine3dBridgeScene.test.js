/**
 * Tests for Engine3D bridge → RT4D descriptor / headless receipt adapter.
 * Status: **partial** (descriptor + receipt only; no path-trace).
 */
import assert from "node:assert/strict";
import { describe, it } from "node:test";
import {
  bridgeSceneToHypersphereDescriptors,
  hashBridgeScene,
  renderEngine3dFrameReceipt,
} from "./engine3dBridgeScene.js";

const tinyScene = {
  schemaVersion: "engine3d-bridge-scene/1.0",
  frameIndex: 0,
  seed: 7,
  primitives: [
    {
      kind: "hypersphere",
      id: "body:a",
      center: [0.1, 0.2, 0.3, 0],
      radius: 0.5,
      source: "body",
      materialHint: "surf",
    },
    {
      kind: "point_sample",
      id: "mesh:v0",
      center: [1, 0, 0, 0],
      radius: 0.08,
      source: "mesh_vertex",
    },
  ],
  camera: {
    eye: [0, 1, 4, 0],
    lookAt: [0, 0, 0, 0],
    up: [0, 1, 0, 0],
    fovY: 0.9,
  },
  lattice: { nodeCount: 0, glyphIntensity: 0, glyphCount: 0, shaderParams: {} },
  mappingNotes: {
    polyMeshTriangles: "declared",
    bodyApproximation: "sphere_from_mass",
    meshVertices: "point_hypersphere_samples_capped",
    lattice: "visualMod_and_optional_mandala_nodes",
  },
};

describe("engine3dBridgeScene adapter", () => {
  it("hashes tiny scene deterministically", () => {
    assert.equal(hashBridgeScene(tinyScene), hashBridgeScene(structuredClone(tinyScene)));
  });

  it("maps primitives to hypersphere descriptors", () => {
    const mapped = bridgeSceneToHypersphereDescriptors(tinyScene);
    assert.equal(mapped.status, "partial");
    assert.equal(mapped.hyperspheres.length, 2);
    assert.equal(mapped.hyperspheres[0].radius, 0.5);
  });

  it("headless receipt is deterministic", () => {
    const evidence = { sceneHash: "abc", frameIndex: 0, seed: 7 };
    const a = renderEngine3dFrameReceipt(tinyScene, evidence);
    const b = renderEngine3dFrameReceipt(tinyScene, evidence);
    assert.equal(a.receiptHash, b.receiptHash);
    assert.equal(a.mode, "null-headless");
    assert.equal(a.imageStatus, "not_rendered_headless");
  });
});
