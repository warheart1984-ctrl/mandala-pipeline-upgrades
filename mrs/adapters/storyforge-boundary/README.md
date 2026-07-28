# StoryForge boundary adapter (MRS)

MRS-side freeze for StoryForge Runtime Spec v1.0 crossing:

**RenderRequest → MRS → RenderResult**

- Ownership: see `BOUNDARY.md`
- Contract tags: see `CONTRACT.md`
- Schemas: `schemas/`
- Validate + route: `validate_request.py`, `route.py`
- Tests: `test_boundary.py`

Status: **partial**. Does not implement StoryForge PromptComposer or IModelBackend.
