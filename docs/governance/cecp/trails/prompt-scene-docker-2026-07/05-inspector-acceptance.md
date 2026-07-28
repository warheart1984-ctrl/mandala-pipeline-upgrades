# 05 — Inspector: Acceptance

**Trail:** `prompt-scene-docker-2026-07`  
**Stage:** Inspector (evidence only; CECP trail write)  
**Worktree:** `G:/Mandala Rendering Software/.worktrees/cecp-docker-rebase`  
**HEAD inspected:** `6b3f37897c04e2126de0d0ce857d0e0bf6367a76` (`tmp/cecp-docker-rebase`)  
**Predecessor:** Reviewer (`04-reviewer-conformance.md`)  
**Verdict:** **FAIL**

---

## 1. Verdict

**FAIL**

Dual-layout `mrs_map` unit tests pass and the repo-root `Dockerfile` statically declares COPY/ENV/bridge+expand smoke lines, but Architect acceptance cannot be closed: Genblaze app import is broken (`app.lattice_polish_defaults` missing), so `test_prompt_to_scene` / ban pytest collectors fail; Docker Desktop daemon is unavailable, so image build and `/health` probes were not run.

---

## 2. Commands run

| Command | Result |
|---------|--------|
| `pytest mrs/adapters/prompt-scene-bridge/test_mrs_map.py -q --tb=line` | **exit 0** — 16 passed, 3 skipped |
| `pytest mrs/apps/genblaze-media/tests/test_prompt_to_scene.py -q --tb=line` | **exit 2** — collection ERROR: `ModuleNotFoundError: No module named 'app.lattice_polish_defaults'` |
| Ban pytest (`test_api.py::test_no_story_forge_imports`, `test_seedance.py::test_seedance_modules_have_no_story_forge`, `test_prompt_to_scene.py::test_ban_note_app_must_not_import_narrative_lane`) | **exit 4** — same `lattice_polish_defaults` collection ERROR on all three |
| Static ban scan: `mrs/apps/genblaze-media/app/*.py` for `story_forge` / `storyforge` | **PASS** — 30 `.py` files, 0 offenders |
| `docker info` | **exit 1** — client OK; daemon: `failed to connect … dockerDesktopLinuxEngine` (pipe missing) |
| `docker build -t mrs-prompt-scene-smoke:inspect .` | **blocked** — same daemon error (not executed) |
| `git ls-remote --heads origin feat/engine3d-genblaze-cinematic-plugin` | **empty** — remote branch appears deleted on GitHub |
| Local refs | HEAD `6b3f378`; local `feat/engine3d-genblaze-cinematic-plugin` → `1153b8c`; stale `origin/feat/…` tip → `6d1a569` (rebase base) |

No push / force-push performed.

---

## 3. Claim ↔ evidence

| Claim | Evidence | Result |
|-------|----------|--------|
| Dual-layout / sibling expand defaults **enforced** | `test_mrs_map.py` 16 passed (incl. ENV override + sibling Docker layout ACs) | **PASS** |
| Genblaze Docker-layout default + ban note tests | `test_prompt_to_scene.py` cannot collect | **FAIL** |
| No `story_forge` / `storyforge` under `app/*.py` | Pytest bans blocked; static scan 0 offenders in 30 `.py` files | **PASS** (static only) |
| Repo-root Docker COPY bridge → `/app/prompt-scene-bridge/` | `Dockerfile` L85–87 `COPY … run_bridge.py`, `mrs_map.py`, `schemas` | **PASS** (static) |
| ENV `/app` bridge + expand paths; expand default off | `PROMPT_SCENE_BRIDGE_SCRIPT`, `ENGINE3D_EXPAND_SCRIPT`, `PROMPT_SCENE_EXPAND_WORLD=0` (L48–50) | **PASS** (static) |
| Build smoke: bridge `--json` | `RUN python /app/prompt-scene-bridge/run_bridge.py … --json` (L131–133) | **UNVERIFIED** (daemon down) |
| Build smoke: `--expand` asserts `objects` length > 0 | `RUN … --expand` + assert (L137–140); ENV stays `0` | **UNVERIFIED** (daemon down) |
| Local image `/health.prompt_scene.available: true` | Not probed | **UNVERIFIED** |
| Live Render health | Not claimed; remains **declared** | **N/A** |
| Docs do not overclaim live deploy | Reviewer + CONTRACT tags; no elevation attempted here | **PASS** |
| App import graph healthy for Genblaze tests | `main.py` L52 imports missing `app.lattice_polish_defaults` (blame `8a7b542`; no matching file in tree) | **FAIL** |

---

## 4. Docker blocker + static Dockerfile proof

**Blocker:** Docker Desktop Linux engine not running (`npipe:////./pipe/dockerDesktopLinuxEngine` missing). Client 29.6.1 present; Server unreachable. Image rebuild and container `/health` cannot be evidenced in this inspection.

**Static proof (repo-root `Dockerfile` at HEAD `6b3f378`):**

- **COPY:** `mrs/adapters/prompt-scene-bridge/{run_bridge.py,mrs_map.py,schemas}` → `./prompt-scene-bridge/`
- **ENV:** `PROMPT_SCENE_BRIDGE_SCRIPT=/app/prompt-scene-bridge/run_bridge.py`; `ENGINE3D_EXPAND_SCRIPT=/app/engine3d-core/scripts/expand-world-document.mjs`; `PROMPT_SCENE_EXPAND_WORLD=0`
- **RUN smoke (bridge stub):** `python /app/prompt-scene-bridge/run_bridge.py --prompt "docker bridge smoke" --json`
- **RUN smoke (expand CLI):** same script with `--expand` + `assert len(objects)>0` while ENV remains `0`

Status for image bundling stays **partial** until a daemon-backed `docker build` + `/health` probe succeed.

---

## 5. Gaps for Implementor

1. **Critical:** Add missing `mrs/apps/genblaze-media/app/lattice_polish_defaults.py` (or remove/revert the `8a7b542` import in `main.py`) so Genblaze test collection works again.
2. Re-run `test_prompt_to_scene.py` and the three ban nodeids after import fix; expect green.
3. Start Docker Desktop; `docker build` repo-root image; confirm bridge + expand smokes; run container and probe `GET /health` → `prompt_scene.available: true`, `expand_world: false`.
4. Do not elevate live Render beyond **declared** without Manual Deploy evidence.
5. Foreman: after this inspector commit on `tmp/cecp-docker-rebase`, fast-forward `feat/engine3d-genblaze-cinematic-plugin` to that commit locally. Remote `origin/feat/engine3d-genblaze-cinematic-plugin` is empty (deleted); no push in this trail.

---

## 6. Claim wording to downgrade

- Implementor §4 claimed `test_prompt_to_scene.py` → 10 passed and ban pytest → 2 passed at this lineage tip — **falsified on clean worktree** (collection error). Treat those rows as **unverified / stale** until re-run after lattice module fix.
- Do not claim Docker image bundling **enforced**; keep **partial**.
- Do not claim Genblaze operator Prompt→Scene readiness beyond **Prepared** while `app.main` cannot import.

---

## 7. Git / remote note

- Inspection branch: `tmp/cecp-docker-rebase` @ `6b3f378` (rebased feature history including `feat(docker): wire Prompt→Scene bridge…`).
- `git ls-remote --heads origin feat/engine3d-genblaze-cinematic-plugin` returned **empty** (branch appears deleted on GitHub).
- Stale local tracking tip `origin/feat/engine3d-genblaze-cinematic-plugin` = `6d1a569` was the rebase base; **no push** performed.
- Main workspace dirty tree / broken Unreal plugin path **not** used for tests.

---

## 8. Acceptance decision

| Field | Value |
|-------|-------|
| Decision | **not accepted** |
| Inspector verdict | **FAIL** |
| Blocking gaps | Missing `lattice_polish_defaults`; Docker daemon unavailable |
| Non-blocking residuals | Static Dockerfile contract looks complete; `mrs_map` green; static ban green |
