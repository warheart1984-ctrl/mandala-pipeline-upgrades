/**
 * ProjCC invariant tests.
 * Status claim under test: partial (not enforced).
 */

import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { vec4 } from "../math/vec4.js";
import { Projector4D } from "../output/projector.js";
import {
  pccFidelityZeroHolds,
  listPccInvariants,
  PCC_INVARIANTS,
  ProjectionKernel,
  createProjectionState,
  resolveObservationPreset,
  createPathTracerProjectionHooks,
  describePathTracerProjectionIntegration,
} from "../projection/index.js";

describe("ProjCC invariants", () => {
  it("catalog exposes PCC ids without enforced tags", () => {
    const list = listPccInvariants();
    assert.ok(list.some((i) => i.id === "PCC-FIDELITY-ZERO"));
    for (const inv of PCC_INVARIANTS) {
      assert.notEqual(inv.status, "enforced");
    }
  });

  it("zero-param fidelity matches Projector4D closed form", () => {
    const point = vec4(1.5, -2, 3.25, 0.75);
    const r = pccFidelityZeroHolds(point, { d4: 4, d3: 4, scale: 80, width: 640, height: 480 });
    assert.equal(r.ok, true, JSON.stringify(r));
  });

  it("ProjectionKernel classic path matches Projector4D at identity params", () => {
    const point = vec4(0.8, 0.2, -0.4, 0.3);
    const k = new ProjectionKernel({ theta: 0, phi: 0, tau: 0, kappa: 0 });
    const classic = k.classicProject3D(point);
    const projector = k.createProjector4D();
    const actual = projector.project4Dto3D(point);
    assert.ok(Math.abs(classic.x - actual.x) < 1e-12);
    assert.ok(Math.abs(classic.y - actual.y) < 1e-12);
    assert.ok(Math.abs(classic.z - actual.z) < 1e-12);
  });

  it("createProjectionState rejects negative kappa", () => {
    assert.throws(() => createProjectionState({ kappa: -1 }), /kappa/);
  });

  it("slice_hyperplane preset maps to W-slice LiveLink policy", () => {
    const r = resolveObservationPreset("slice_hyperplane", { tau: 0.25 });
    assert.equal(r.projectionPolicyId, 1);
    assert.equal(r.state.tau, 0.25);
  });

  it("path-tracer hooks remain declared and unwired", () => {
    const hooks = createPathTracerProjectionHooks({ modeId: "perspective_w", width: 320, height: 240 });
    assert.equal(hooks.status, "declared");
    assert.equal(hooks.wiredIntoPathTracer4D, false);
    const d = describePathTracerProjectionIntegration();
    assert.equal(d.wired, false);
  });

  it("Projector4D remains importable SoT (no parallel print kernel)", () => {
    const p = new Projector4D({ d4: 4 });
    const q = p.project4Dto3D(vec4(1, 0, 0, 0));
    assert.equal(q.x, 1);
  });
});
