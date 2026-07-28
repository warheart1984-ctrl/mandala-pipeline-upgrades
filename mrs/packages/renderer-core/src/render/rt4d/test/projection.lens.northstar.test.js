/**
 * Hyper-Caustic Lens north-star / verifier hooks.
 * Soft-skip when no reference dataset — do not claim visual FULL_PASS.
 */

import { describe, it } from "node:test";
import assert from "node:assert/strict";
import {
  verifyHyperCausticLensFactory,
  verifyHyperCausticLensNorthStar,
  verifyHyperCausticLensProjectionHook,
  runHyperCausticLensVerifierSuite,
  HYPER_CAUSTIC_VERIFIER_STATUS,
} from "../projection/index.js";

describe("HyperCausticLensVerifier", () => {
  it("factory hook loads official validation scene", () => {
    const r = verifyHyperCausticLensFactory({ width: 64, height: 48 });
    assert.equal(r.ok, true);
    assert.equal(r.verdict, "pass");
    assert.equal(r.status, HYPER_CAUSTIC_VERIFIER_STATUS);
  });

  it("projection structural hook yields finite screen sample", () => {
    const r = verifyHyperCausticLensProjectionHook({ width: 64, height: 48 });
    assert.equal(r.ok, true);
    assert.equal(r.verdict, "pass");
  });

  it("north-star soft-skips without reference dataset", () => {
    const r = verifyHyperCausticLensNorthStar({});
    assert.equal(r.verdict, "soft_skip");
    assert.equal(r.ok, true);
    assert.match(r.reason, /soft-skip/i);
  });

  it("north-star passes when hashes match", () => {
    const r = verifyHyperCausticLensNorthStar({
      referenceHash: "abc",
      candidateHash: "abc",
    });
    assert.equal(r.verdict, "pass");
    assert.equal(r.ok, true);
  });

  it("north-star fails when hashes differ", () => {
    const r = verifyHyperCausticLensNorthStar({
      referenceHash: "abc",
      candidateHash: "xyz",
    });
    assert.equal(r.verdict, "fail");
    assert.equal(r.ok, false);
  });

  it("suite ok when north-star soft-skips", () => {
    const suite = runHyperCausticLensVerifierSuite({ width: 64, height: 48 });
    assert.equal(suite.ok, true);
    assert.equal(suite.status, "declared");
    assert.ok(suite.results.some((r) => r.verdict === "soft_skip"));
  });
});
