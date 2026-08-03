# RT4D GPT Action (ChatGPT Plus) — Setup & Usage

> Status: **partial** — dimensional previews, not photoreal anime. Provenance and
> determinism are enforced; preview fidelity is not.
> Commit: `e828864` (branch `feat/rt4d-chatgpt-plugin`)

## What this is

A ChatGPT-compatible REST/OpenAPI façade on the existing MCP gateway so ChatGPT
Plus (which cannot import raw MCP servers) can drive RT4D via **GPT Actions**.

```
ChatGPT Plus → GPT Action (OpenAPI) → API Gateway → MCP tool handlers → ECS renderer → PNG + evidence
```

The façade reuses the MCP tool logic (`createScene`, `performRender`,
`resolveScene`, `applySceneUpdate`). No separate service.

## Endpoints (dev)

| Item | Value |
|------|-------|
| OpenAPI schema (import URL) | `https://zs8hkz982h.execute-api.us-east-2.amazonaws.com/dev/openapi.json` |
| Base URL | `https://zs8hkz982h.execute-api.us-east-2.amazonaws.com/dev` |
| `POST /v1/scenes` | Create scene (deterministic sceneId from prompt) |
| `GET /v1/scenes/{sceneId}` | Inspect scene + provenance |
| `PATCH /v1/scenes/{sceneId}` | Update rotations / projection / re-preview |
| `POST /v1/scenes/{sceneId}/render` | Render preview → pre-signed S3 PNG URL |

Auth: `Authorization: Bearer <api key>` on every call except `/openapi.json`
and `/health` (open). The authorizer reads the key fresh from Secrets Manager
`mrs-rt4d-dev/api-keys` and is fail-closed.

## ChatGPT setup

1. Create/Open a GPT → **Configure** → **Actions** → **Create new action**.
2. Authentication: **API Key**, type **Bearer**. Paste the **key value only**
   (ChatGPT prepends `Bearer `). Do not paste the key into prompts, instructions,
   or the schema.
3. Import the schema from the OpenAPI URL above (or paste the JSON from
   `infra/cdk/lambda/mcp-handler/openapi.json`).
4. Save, then test with a prompt like: *"Create a cinematic gothic cathedral
   scene at dusk and render a preview."*

### GPT instructions (suggested text)

```
You can create deterministic 4D scenes and render dimensional previews.

Call order:
1. create_rt4d_scene — prompt → sceneId (same prompt always returns the same sceneId)
2. render_rt4d_preview — sceneId → data.previewUrl (pre-signed HTTPS PNG,
   render it as an image, not raw JSON)
3. inspect_rt4d_scene — for recovery or provenance when a sceneId is known

When the user gives only a sceneId, inspect it before rendering.
To adjust a scene, use update_rt4d_scene (rotations xw/yw/zw, projection d4/d3,
rePreview=true to re-render) — the sceneId stays stable.

Response envelope: { ok, statusTag, data, error }. statusTag is "partial":
previews are dimensional renderings, not photoreal anime.
```

## Verified behavior (2026-08-03, live)

- `GET /openapi.json` → 200, OpenAPI 3.0.3 with the three paths.
- Same prompt twice → identical sceneId (replayable/deterministic).
- `POST /v1/scenes/{id}/render` → `data.previewUrl` is a pre-signed S3 URL to
  the PNG (`mrs-rt4d-dev-renders`), `data.sha256` matches across re-renders,
  and the URL returns HTTP 200 with PNG magic bytes.
- `PATCH` update returns the stable sceneId plus a fresh preview when requested.
- MCP transport (`/mcp`) still works (initialize → `rt4d-hybrid-anime-production` v0.2.0).

## Key rotation

The dev API key was rotated on 2026-08-03. Current key lives only in Secrets
Manager (`mrs-rt4d-dev/api-keys`) and in ChatGPT's auth field. Rotate by:
writing `{"keys":["<new>"]}` to the secret (use a JSON file + `--secret-string
file://...` — PowerShell/CLI strip embedded quotes otherwise), then replace the
value in ChatGPT. Never commit the key.

## Related files

- `infra/cdk/lambda/mcp-handler/index.mts` — shared ops + REST dispatch
- `infra/cdk/lambda/mcp-handler/openapi.json` — GPT Action schema (SoT)
- `infra/cdk/lib/mcp-gateway-stack.ts` — routes / auth wiring
- `infra/cdk/lambda/authorizer/index.ts` — bearer authorizer (stage-wide policy)
