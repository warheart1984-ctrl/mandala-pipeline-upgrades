# Printer Service API — `/printer` contract

> **Status:** **partial** — HTTP routes enforced in Genblaze tests; live execute
> opt-in via `PRINTER_API_ENABLED=1`. MCP = capability stubs (**skeleton**).  
> **App:** `mrs/apps/genblaze-media`  
> **Provider:** `app/printer_provider.py`  
> **Trail:** `digital-printer-v2-2026-07` (prior: `printer-mode-renderer-2026-07`)

## Base URL

`/printer`

## Endpoints

### `GET /printer/health`

Deterministic health (no execute). Also mirrored under main `GET /health` → `printer`.

### `POST /printer/print`

Runs the deterministic print pipeline.

**Query:** `dry_run=true` — sovereignty + evidence only (no Node).

**Env:** `PRINTER_API_ENABLED=1` required for live execute; `MRS_PRINT_TIMEOUT_SECONDS` (fallback `MRS_RENDER_TIMEOUT_SECONDS`, default 900).

**Body (RenderRequest):** full RenderRequest JSON (preferred).

**Body (compact):**

```json
{
  "scene": { "...SceneSpecification..." },
  "surfaces": { "aovs": ["beauty"] },
  "samples": 16,
  "quality": "print_hq",
  "denoise": true,
  "softPenumbra": true
}
```

**Quality profiles (all enforced params):** `print_fast` | `print_hq` | `print_cinematic` | `print_reference`

| Profile | denoise | softPenumbra |
|---------|---------|--------------|
| print_fast | false | false |
| print_hq / cinematic / reference | true | true |

**Response:**

```json
{
  "beauty": "<base64 or null on dry-run>",
  "evidence": { },
  "lineage": { },
  "hash": "sha256-..."
}
```

### `POST /printer/validate`

Validates surface contract + SceneSpec / RenderRequest.

```json
{ "ok": true, "violations": [] }
```

### `POST /printer/provenance`

Returns evidence / lineage / provenance frames for a print or dry-run.

## MCP capabilities (skeleton)

File: `mrs/apps/genblaze-media/app/printer_mcp_capabilities.json`

| Capability | HTTP |
|------------|------|
| `printer.print_surface` | `POST /printer/print` |
| `printer.validate_scene` | `POST /printer/validate` |
| `printer.get_evidence` | `POST /printer/provenance` |
| `printer.get_lineage` | `POST /printer/provenance` |

## Deploy notes

- Root `Dockerfile` must COPY `storyforge-boundary/printer/` + `governance/` + `run_print.py`.
- Render Blueprint (`render.yaml`): set `PRINTER_API_ENABLED=1`.
- Preferred health check path for printer service: `/printer/health` (also under `/health`).
- **Render MCP:** not available in this Cursor session — deploy via dashboard / CLI; do not fake a live URL.
