# StoryForge Boundary Adapter — Contract

> **Status:** **partial** — schema validation **enforced** by unit tests in this
> package; deep render execution routes remain **skeleton** / **declared**.
> End-to-end StoryForge Runtime Spec v1.0 is **not** claimed enforced.

## Purpose

Validate MRS intake `RenderRequest` JSON and route to existing MRS paths **or**
return an honest skeleton / refuse result. Does **not** implement StoryForge
PromptComposer, IModelBackend, or RenderIntentBuilder.

Authoritative ownership: `BOUNDARY.md`.

## RenderRequest (**partial** → validate **enforced**)

See `schemas/RenderRequest.schema.json`.

Required: `schemaVersion` (`1.0`), `requestId`, `intentId`, `worldId`,
`payload.route`, `payload.render`.

Banned on intake (validator): top-level or payload keys that smuggle mutable
SF-owned bodies (`promptSpec`, `renderIntent`, `promptComposer`, `modelBackend`).
Opaque hashes under `provenance` are allowed.

## RenderResult (**partial**)

See `schemas/RenderResult.schema.json`.

`status`: `ok` | `error` | `refused`. Provenance echoes intake ids. Artifacts
optional until a deep route is wired.

## Routes

| `payload.route` | Behavior this trail | Tag |
|-----------------|---------------------|-----|
| `scene-spec` | Accept embedded `sceneSpecification`; echo in result mapping | **partial** |
| `engine3d-world` | Accept/echo `engine3dWorldDocument` if present; else refuse | **skeleton** |
| `proton-raster` | Note mapping to proton-raster-bridge shape; no pipeline run | **skeleton** |
| `rt4d` | Note mapping; no RT4D execute in this adapter | **skeleton** |

## Ban

- No StoryForge package imports in this adapter’s runtime path for Genblaze app.
- Genblaze `app/*.py` string ban unchanged (existing tests).

## Status tags summary

| Artifact | Tag |
|----------|-----|
| BOUNDARY.md | **partial** (ownership freeze documented) |
| schemas | **partial** (shapes + unit validate; not full CI schema suite) |
| `validate_request.py` | **enforced** (unit tests) |
| `route.py` deep execution | **skeleton** |
| SF PromptComposer / IModelBackend | **declared** (owner StoryForge — not in MRS) |
