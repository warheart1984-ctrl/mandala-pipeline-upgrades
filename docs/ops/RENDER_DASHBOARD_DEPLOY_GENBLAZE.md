# Render dashboard — Genblaze media (hackathon demo)

Operator checklist for the live App URL on Render. Evidence-bound; no secrets in git.

## Service

| Item | Value |
|------|-------|
| Blueprint | repo-root `render.yaml` |
| App | `mrs/apps/genblaze-media` |
| Health | `GET /health` → `status: ok` |
| Typical URL | `https://mandala-rendering-system-mrs.onrender.com/` |

## Env vars (dashboard)

**Required for B2 persistence**

- `B2_KEY_ID`, `B2_APPLICATION_KEY` (or `B2_APP_KEY`), `B2_BUCKET`, `B2_REGION`

**Hackathon fan-out (optional but judge-facing)**

- `GMI_API_KEY` — GMI Cloud credits (eligible Devpost participants)
- `GENBLAZE_GMI_IMAGE_MODEL` — default `seedream-5.0-lite`
- Optional: `GMI_BASE_URL` (queue endpoint only — **not** the `/v1` chat URL)

**Demo cache (pre-render → B2)**

- `GENBLAZE_DEMO_CACHE=1`
- `GENBLAZE_DEMO_CACHE_SHOT=<shot_id>`
- `GENBLAZE_DEMO_CACHE_FRAME=0`

**Free fallback polish**

- `GENBLAZE_POLISH_ENABLED=1`
- `GENBLAZE_POLISH_BACKEND=auto` (cascade: gmi → fal → nvidia → hfspace)
- `GENBLAZE_HFSPACE_URL` (default Space URL is fine)

**Armed / optional**

- `NVIDIA_API_KEY`, `FAL_KEY`
- `GENBLAZE_IMAGE_BACKEND=rt4d` for deterministic structure stills without NIM

Never paste keys into git, screenshots of `.env`, or PR bodies.

## Pre-render off-box

Free Render instances are a poor place to burn 24h of GMI gens. Run
`python -m app.pre_render … --upload-b2` on a laptop/VM with credits, then
point the Render service at the same bucket with `GENBLAZE_DEMO_CACHE=1`.

See [`HACKATHON_DEMO_CACHE_B2.md`](./HACKATHON_DEMO_CACHE_B2.md).

## Deploy steps

1. Push branch / merge to the connected GitHub repo.
2. Render → Manual Deploy (free tier does not always auto-deploy).
3. Confirm `/health`: `b2_configured`, `demo_cache`, `provider_cascade`, `gmi`.
4. Smoke: `POST /api/generate` with `demo_cache=true` after frames exist in B2.

## Gaps (honest)

| Gap | Status |
|-----|--------|
| GMI credits / key on Render | Operator must set; not in CI |
| `genblaze-gmicloud` in Docker image | Add optional install if image lacks it |
| Live NIM 504s | Known; prefer RT4D + demo cache for demos |
| B2 Class C | Keep `B2_PROBE_ON_HEALTH=0` on free tier |
