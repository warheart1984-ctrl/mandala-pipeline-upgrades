# StoryForge boundary adapter (MRS)

MRS-side freeze + **v1.0 shippable path** for StoryForge Runtime Spec crossing:

**RenderRequest → MRS → RenderResult** (optional PNG + SHA-256)

- Ownership: `BOUNDARY.md`
- Contract (enforced vs declared): `CONTRACT.md`
- Schemas: `schemas/`
- Validate / route / execute: `validate_request.py`, `route.py`, `execute.py`, `paths.py`
- CLI: `run_pipeline.py`
- Smoke: `smoke_pipeline.py` → `output/storyforge-pipeline-smoke.png`
- Tests: `test_boundary.py`, `test_pipeline.py`

```text
python run_pipeline.py -r fixtures/sample-render-request-executable.json --execute --out-dir ../../../../output --json
```

Status: **partial**. Does not implement StoryForge PromptComposer or IModelBackend.
