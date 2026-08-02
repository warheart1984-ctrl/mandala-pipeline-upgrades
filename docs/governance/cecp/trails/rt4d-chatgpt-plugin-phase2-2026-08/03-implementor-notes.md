# Implementor notes — RT4D ChatGPT plugin Phase 2

**Trail:** `rt4d-chatgpt-plugin-phase2-2026-08`  
**Status tags:** MCP bridge **partial**; widget **partial**; ChatGPT embedded UI host-dependent; export / RT3D persistence / directory **declared**

## Intent

Ship interactive dimensional preview viewer + `update_rt4d_scene` wiring for PR continuation after Phase 1 (#100 merged).

## Files touched

- `mrs/apps/rt4d-chatgpt-plugin/widget/` — React + Vite + Three.js viewer → `dist/rt4d-viewer.html`
- `mrs/apps/rt4d-chatgpt-plugin/server/src/tools/update-rt4d-scene.ts` — rotations/projection update + optional rePreview
- `mrs/apps/rt4d-chatgpt-plugin/server/src/scene-store.ts` — `updateRt4dSceneRecord`
- `mrs/apps/rt4d-chatgpt-plugin/server/src/index.ts` — `ui://rt4d/viewer-v1`, widget meta on create/render/update/inspect
- README + SKILL.md + plugin.json honesty updates
- Contract tests extended

## Tests

- `server/npm test` — 4/4 pass
- `widget/npm run build` + `typecheck` — pass

## Gaps (Phase 3)

- `export_rt4d_asset` still skeleton
- No durable store / verified continuity / AnimeStylizer
- ChatGPT directory listing not claimed

## Debt — portrait lighting API mismatch (**declared**)

**Bug-prevention / do not wire without adapter.**

- `createPortraitLightingRig` (renderer-core) returns a **portrait object**
  (`keyLight` / `fillLight` / `rimLight` / `envLight`).
- `Scene4D.setLightRig` expects an **array** of RT4D lights (`lightRig.map(...)`).
- Passing the portrait object into `setLightRig` would throw or silently mis-bind.

**Current path:** RT4D engine / plugin preview use the audited `render-still.mjs` light list; do **not** call `createPortraitLightingRig` → `setLightRig` until an adapter exists.

**Status:** debt **declared** (not fixed in this trail).
