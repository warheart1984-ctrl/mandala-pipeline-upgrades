# 03 Implementor notes

## Delivered

- `demo_cache.py`, `provider_cascade.py`, `gmi_provider.py`, `pre_render.py`
- Config/env: `GENBLAZE_DEMO_CACHE*`, `GMI_*`
- `POST /api/generate` demo_cache path + source labels
- `/health`: `gmi`, `provider_cascade`, `demo_cache`
- Docs: `HACKATHON_DEMO_CACHE_B2.md`, deploy, Devpost pitch
- Tests: `tests/test_demo_cache.py`

## Status tags

| Piece | Tag |
|-------|-----|
| Cache keying + labels | **enforced** (unit tests) |
| Live GMI generate | **partial** (needs SDK + key) |
| Demo cache B2 I/O | **partial** (needs credentials) |
| hfspace fallback | **partial** (existing polish path) |

## Gaps

- Docker image may lack `genblaze-gmicloud` until optional install
- No live credit spend in CI
