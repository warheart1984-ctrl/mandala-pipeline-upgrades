// @mrs/rt4d-engine acceptance tests — status: live
// Run with `pnpm --filter @mrs/rt4d-engine test` (tsx --test). Imports .ts directly.
import assert from "node:assert/strict";
import { describe, it, before, after } from "node:test";
import { createEngineServer } from "../src/index.ts";

const SPEC = {
  surface: "trefoil-4d",
  resolution: 12,
  rotations: [],
  projection: { type: "perspective", distance4d: 4, distance3d: 4 },
  camera: { fovX: 52, fovY: 52, fovZ: 8, fovW: 8, lensRadius: 0 },
};

const server = createEngineServer().listen(0);
const port = server.address().port;
const base = `http://127.0.0.1:${port}`;

after(() => server.close());

function post(pathname, body) {
  return fetch(`${base}${pathname}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  });
}

function get(pathname) {
  return fetch(`${base}${pathname}`, { method: "GET" });
}

const PNG_MAGIC = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];
function isPng(buf) {
  const b = Buffer.isBuffer(buf) ? buf : Buffer.from(buf);
  for (let i = 0; i < PNG_MAGIC.length; i++) {
    if (b[i] !== PNG_MAGIC[i]) return false;
  }
  return true;
}

before(async () => {
  assert.equal(server.listening, true);
});

describe("rt4d-engine acceptance criteria", () => {
  it("AC1 /health returns a live envelope", async () => {
    const res = await get("/health");
    assert.equal(res.status, 200);
    const env = await res.json();
    assert.equal(env.statusTag, "live");
    assert.equal(env.ok, true);
    assert.equal(env.data.service, "@mrs/rt4d-engine");
  });

  it("AC2 POST /v1/scenes deterministically creates the same sceneId for equal specs", async () => {
    const r1 = await post("/v1/scenes", SPEC);
    const r2 = await post("/v1/scenes", SPEC);
    assert.equal(r1.status, 200);
    assert.equal(r2.status, 200);
    const e1 = await r1.json();
    const e2 = await r2.json();
    assert.equal(e1.statusTag, "live");
    assert.equal(e2.statusTag, "live");
    assert.equal(e1.data.sceneId, e2.data.sceneId);
    assert.ok(e1.data.sceneId.startsWith("rt4d-scene-"));
    assert.equal(e1.data.sceneId.length, 16 + "rt4d-scene-".length);
  });

  it("AC3 POST /v1/scenes/{id}/render with seed returns a PNG + sha256 receipt", async () => {
    const created = await post("/v1/scenes", SPEC);
    const { data } = await created.json();
    const res = await post(`/v1/scenes/${data.sceneId}/render`, { seed: 42, width: 128, height: 128 });
    assert.equal(res.status, 200);
    const env = await res.json();
    assert.equal(env.statusTag, "live");
    assert.match(env.data.renderReceipt.sha256, /^[0-9a-f]{64}$/);
    const png = Buffer.from(env.data.pngBase64, "base64");
    assert.ok(isPng(png), "response pngBase64 must start with PNG magic bytes");
    assert.ok(png.length > 67, "PNG must carry a non-empty IDAT (real pixels, not empty)");
    assert.equal(env.data.renderReceipt.cached, false);
  });

  it("AC4 POST /v1/scenes/{id}/render without seed returns 400", async () => {
    const created = await post("/v1/scenes", SPEC);
    const { data } = await created.json();
    const res = await post(`/v1/scenes/${data.sceneId}/render`, {});
    assert.equal(res.status, 400);
    const env = await res.json();
    assert.equal(env.ok, false);
    assert.ok(env.error?.code === "MISSING_SEED");
  });

  it("AC5 same seed + params reproduces byte-identical PNG; retry is served from cache", async () => {
    const created = await post("/v1/scenes", SPEC);
    const { data } = await created.json();
    const params = { seed: 7, width: 128, height: 128 };

    const r1 = await post(`/v1/scenes/${data.sceneId}/render`, params);
    const e1 = await r1.json();

    const r2 = await post(`/v1/scenes/${data.sceneId}/render`, params);
    const e2 = await r2.json();

    assert.equal(r1.status, 200);
    assert.equal(r2.status, 200);
    assert.equal(e1.data.pngBase64, e2.data.pngBase64, "deterministic seed must produce byte-identical PNG");
    assert.equal(e2.data.renderReceipt.sha256, e1.data.renderReceipt.sha256);
    assert.equal(e2.data.renderReceipt.cached, true);
    const prov = await get(`/v1/scenes/${data.sceneId}/provenance`);
    const penv = await prov.json();
    assert.equal(penv.statusTag, "live");
    // Shared in-memory store: other tests (AC3) may have written receipts for a
    // different seed on the SAME sceneId. Filter to THIS renderKey to verify the
    // cache hit did not duplicate the seed-7 entry.
    const matching = penv.data.receipts.filter((r) => r.renderKey === e1.data.renderKey);
    assert.equal(matching.length, 1);
    assert.equal(matching[0].cached, false);
    assert.equal(matching[0].sha256, e1.data.renderReceipt.sha256);
  });

  it("AC7 /render returns an evidence envelope that verifies via the invariant conformance suite", async () => {
    const engineMod = await import("../src/index.ts");
    const evMod = await import("../src/evidence/rt4dEvidenceEnvelope.ts");
    const created = await post("/v1/scenes", SPEC);
    const { data } = await created.json();
    const res = await post(`/v1/scenes/${data.sceneId}/render`, { seed: 99, width: 128, height: 128 });
    const env = await res.json();
    const ev = env.data.evidence;
    assert.equal(ev.operation, "rt4d_dimensional_preview");
    assert.equal(ev.source, "mrs-renderer-core/rt4d");
    assert.equal(typeof ev.runId, "string");
    assert.equal(ev.seed, 99);
    assert.match(ev.sceneSpecHash, /^[0-9a-f]{64}$/);
    assert.match(ev.renderKey, /^[0-9a-f]{64}$/);
    assert.equal(ev.pngSha256, env.data.renderReceipt.sha256);
    assert.match(ev.replayToken, /^[0-9a-f]{64}$/);

    const verification = evMod.verifyRt4dEvidenceEnvelope(ev);
    assert.equal(verification.ok, true, JSON.stringify(verification.report));

    void engineMod;
  });

  it("AC6 GET /v1/scenes/{id}/geometry returns triangulated surface topology", async () => {
    const created = await post("/v1/scenes", SPEC);
    const { data } = await created.json();
    const res = await get(`/v1/scenes/${data.sceneId}/geometry`);
    assert.equal(res.status, 200);
    const env = await res.json();
    assert.equal(env.statusTag, "live");
    const geo = env.data.geometry;
    assert.ok(Array.isArray(geo.vertices));
    assert.ok(Array.isArray(geo.indices));
    assert.ok(Array.isArray(geo.edges));
    assert.ok(geo.vertices.length > 0, "sampled surface must produce vertices");
    assert.ok(geo.indices.length > 0, "sampled surface must produce triangle faces");
    for (const v of geo.vertices) {
      assert.equal(typeof v.x, "number");
      assert.equal(typeof v.y, "number");
      assert.equal(typeof v.z, "number");
      assert.equal(typeof v.w, "number");
    }
  });
});
