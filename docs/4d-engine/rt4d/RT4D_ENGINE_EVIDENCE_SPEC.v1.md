# RT4D Engine Evidence Envelope — Spec v1

| Field | Value |
|-------|-------|
| `id` | `rt4d.engine.evidence.v1` |
| **Status** | **declared** (CIEMS-aligned, substrate-level) |
| **Layer** | MRS substrate (`mrs/packages/rt4d-engine`) — the *host* repo for this envelope |
| **Canonical consumer** | External CIEMS / Constitutional Runtime (JCR) on Drive-G (`G:\CIEMS`, `G:\.codex\cse\constitutional-runtime`) — not present in this repo |
| **Verification layer** | MRS-local invariant conformance suite (`renderer-core` `runInvariantConformanceSuite`, `validateEvidenceRecord`) |
| Authority | Drive-G-1 (evidence-bound claims). This document is an agreement, not a charter amendment. |
| References | `docs/governance/DIMENSIONAL_COMPRESSION.md` (§2.3 Execution Layer; §4.3 do not invent implementations), `docs/governance/esfr/test-matrix.esfr.md` (CIEMS alignment = declared unless CIEMS artifacts exist here) |

> **Honest scope.** The RT4D engine in this repo renders deterministic 4D path-traced stills
> (`POST /v1/scenes/{id}/render`) and emits the evidence envelope below as a **substrate-level
> artifact**. This envelope is *shaped* to be ingestible by the external CIEMS/JCR runtime, but
> **this repo does not host that runtime**: there is no JCR here, no CIIMS policy gate here, and
> no cross-repo promotion is performed here. Claiming otherwise would be a fake implementation.
> The CIEMS-aligned claim is **declared** — it becomes **tested** or **enforced** only when an
> artifact in `G:\CIEMS` / `G:\.codex\cse\constitutional-runtime` cites it.

---

## 1. Why this exists

Per `DIMENSIONAL_COMPRESSION.md`, the Execution Layer compresses invariants into *executable artifacts*: contracts, schemas, engines, trails, CLI pipelines, host adapters. The evidence envelope is the executable artifact that binds a single RT4D render operation to the constitutional chain

```
Authority → Validation → Decision → Evidence → Verification → Replay → Audit
```

A render is not a "tool call" once it is emitted with this envelope: it becomes a **governed artifact** that a downstream CIEMS host can verify, replay, and audit without re-running the agent that produced it — provided the same `(sceneSpecHash, seed, parametersHash)` triple is supplied (the `replayToken`).

---

## 2. Envelope shape

Produced by `mrs/packages/rt4d-engine/src/evidence/rt4dEvidenceEnvelope.ts` (function
`createRt4dEvidenceEnvelope`) and returned in the `POST /v1/scenes/{id}/render` response as the
`evidence` field.

```ts
type Rt4dEvidenceEnvelope = {
  operation: "rt4d_dimensional_preview";        // declared operation identifier
  source: "mrs-renderer-core/rt4d";             // the renderer-core RT4D CPU path tracer
  engineVersion: string;                        // rt4d-engine package version
  intentId: string;                             // governance: originating intent
  timelineId: string;                           // governance: originating timeline
  worldId: string;                              // governance: originating world
  sceneId: string;                              // engine content-addressed id ("rt4d-scene-<16hex>")
  sceneSpecHash: string;                        // sha256Hex(canonicalRt4dJson(spec)) (key-sorted)
  sceneSha256: string;                          // sha256(canonicalSceneJson(spec)) (engine internal)
  runId: string;                                // monotonic "run-N" within the engine process
  renderKey: string;                            // engine content-add render key
  seed: number;                                 // deterministic uint32 rng seed (P4)
  pngSha256: string;                            // sha256 of the rendered PNG bytes
  parameters: { seed, maxDepth, samplesPerPixel, width, height, timeSeconds };
  parametersHash: string;                       // sha256Hex(parameters)
  at: string;                                   // ISO-8601 emit time (audit only)
  replayToken: string;                          // sha256(sceneSpecHash:seed:parametersHash)
};
```

### Field derivation rules (must not drift)

| Field | Formula |
|-------|---------|
| `sceneSpecHash` | `sha256Hex(sceneSpec)` → key-sorted canonical JSON (renderer-core `canonicalRt4dJson`) |
| `sceneSha256` | engine-internal `sha256Hex(canonicalSceneJson(spec))`, `lensRadius` normalized to 0 |
| `renderKey` | `sha256Hex(sceneHash + JSON.stringify(orderedParams))` (engine receipt key) |
| `seed` | deterministic uint32 derived from `sceneSha256` by the caller (`mrs/apps/rt4d-chatgpt-plugin` `deriveSeed`) — never `Date.now()` |
| `replayToken` | `sha256(sceneSpecHash + ":" + seed + ":" + parametersHash)` — the single value a CIEMS replay gate compares |

### Determinism obligations (P4 replayable reality)

- `seed` drives **all** path-tracer randomness (`mulberry32(seed)` injected into `PathTracer4D`).
- `lensRadius` is forced to 0 (the `Camera4D` DOF lens otherwise calls `Math.random()`).
- The hyperplane sample is fixed at the central 4D slice (`generateRay(x, y, u1, u2, 0.5, 0.5)`) so finite hyperspheres do not speckle.
- Same `(sceneSpecHash, seed, parameters)` ⇒ byte-identical PNG ⇒ identical `pngSha256` and `replayToken`.

---

## 3. Verification (substrate level)

`verifyRt4dEvidenceEnvelope(envelope)` in `rt4dEvidenceEnvelope.ts`:

1. Runs the renderer-core invariant conformance suite for the in-process RT4D adapter
   (`runInvariantConformanceSuite({ id: "rt4d-dimension-render" })`), covering foundational
   (`PI-GEO-LENGTH`, `PI-CALC-ENERGY`, `PI-TRIG-RADIAL`) and engine invariants.
2. Validates every emitted `EvidenceRecord` via `validateEvidenceRecord`.
3. Anchors the render to the foundational invariant `PI-GEO-LENGTH` (4D length preservation,
   the same invariant `render-still.mjs` checks) via `createEvidenceRecord`, with
   `evidenceAnchors = [sceneSpecHash, renderKey, pngSha256]` and `runtimeId = source`.
4. Returns `ok = allFoundationalPassed && recordsValid && PI-GEO-LENGTH verdict == "pass"`.

This is the **MRS substrate verification** step. It does **not** assert CIEMS/JCR enforcement —
see §5. The `report` shape returned is `{ envelope, recordsValid, conformancesummary,
allFoundationalPassed, evidenceRecord }`.

---

## 4. Replay contract (for the external CIEMS/JCR host)

To replay-verify a prior render, the CIEMS host supplies the *exact* envelope fields and asks
the engine to re-render. Acceptance:

- `replayToken` matches the stored token.
- The re-rendered `pngSha256` equals the envelope's `pngSha256`.
- `verifyRt4dEvidenceEnvelope` returns `ok: true`.

Because the engine is content-addressed and seed-driven, a replay with the same
`(sceneSpecHash, seed, parameters)` is guaranteed byte-identical without re-running the plugin.

---

## 5. Relationship to CIEMS / JCR (drive-G external)

| Artifact | Where it lives | Status in *this* repo |
|----------|----------------|----------------------|
| CIEMS Constitutional Runtime / JCR | `G:\CIEMS`, `G:\.codex\cse\constitutional-runtime` | **not present** (declared-only) |
| Sovereign X OS / CIEMS namespace | `G:\Sovereign-X-Constitutional-Compute` | **not present** (declared-only) |
| CIEMS lineage tree / promotion | `docs/governance/cecp/trails/*` | **declared** (no runtime gate) |
| This evidence envelope | `mrs/packages/rt4d-engine` | **declared** envelope; verification = **tested** (conformance suite passes) |

Concretely: this envelope is *ready to be cited* by a CIEMS promotion packet, but the packet
itself would be authored in the CECP trail repo and admitted by the Drive-G CIEMS runtime — a
separate, explicitly-mandated operation. Do not claim "CIEMS enforcement" from this repo alone.

---

## 6. Non-goals / honesty boundary

- This envelope does **not** claim the engine is CIEMS-certified, Phase-4 photoreal, or a
  "constitutional compute node". Those are promotion claims.
- The envelope carries `intentId`/`timelineId`/`worldId` for lineage, but **does not** assert
  cross-world federation or multi-tenant governance — those remain declared (`CONSTITUTIONAL_LAYER_STACK.md`).
- `operation: "rt4d_dimensional_preview"` is scoped to still-image dimensional preview only.
  Animation, timeline, and export remain declared (`render_rt4d_preview` status `partial` at the
  product-lane level).
