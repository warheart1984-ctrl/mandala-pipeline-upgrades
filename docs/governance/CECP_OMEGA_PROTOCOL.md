# Constitutional Engineering Crew Protocol (CECP Ω∞)

> **Status (MRS local):** **partial** — five-role crew skills exist and require permanent
> trail artifacts under `docs/governance/cecp/trails/`. Full org-wide enforcement of
> trail writes is not claimed until CI gates exist.
>
> **Status (cross-project):** **declared** only — Research OS, PARAGON One,
> Sovereign X OS, CIEMS, DAR-Z adoption is roadmap language, not present capability.
>
> **Authority:** Drive-G-1 (evidence-bound claims) · Drive-G-2 (maturity dimensions) ·
> MRS `AGENTS.md` (P1–P5). This protocol does **not** amend the constitutional charter.

---

## 1. Purpose

CECP Ω∞ is the default **crew workflow** for Mandala Rendering Software (MRS): a
governed lineage from architecture through acceptance where every stage leaves a
**permanent, independently verifiable evidence trail**.

It turns Prompt→Scene-class work from “a feature that shipped” into a **governed
reference implementation** with replayable stage artifacts.

## 2. Principles

| # | Principle | Meaning |
|---|-----------|---------|
| C1 | **Replayable** | Stage outputs are written to the repo (or named trail id) so a later agent/human can reconstruct decisions without chat memory. |
| C2 | **Independently verifiable** | Inspector verdicts cite commands, paths, and claim↔evidence rows — not author reputation. |
| C3 | **Constitutionally governed** | Roles obey `AGENTS.md` / charter principles; protected paths stay off-limits unless the user explicitly authorizes. |
| C4 | **Evidence-bound claims** | Status tags (**enforced** / **partial** / **declared** / **skeleton**) must match tests and code (Drive-G-1). |
| C5 | **Lineage over heroics** | Architecture → Build → Implementation → Review → Inspection → Acceptance. Skip stages only when the user narrows scope. |

## 3. Role definitions and required artifacts

| Stage | Role | Writes product code? | Required trail artifact(s) |
|-------|------|----------------------|----------------------------|
| 1 | **Architect** | No | `01-architect-adr.md` — ADR + interface specification + constitutional boundary analysis |
| 2 | **Builder** | Stubs / scaffolds only | `02-builder-scaffold-manifest.md` — scaffold manifest, dependency graph, build-artifacts inventory |
| 3 | **Implementor** | Yes | `03-implementor-notes.md` — production implementation notes + unit/integration test inventory |
| 4 | **Reviewer** | No | `04-reviewer-conformance.md` — constitutional conformance, standards compliance, policy validation |
| 5 | **Inspector** | No | `05-inspector-acceptance.md` — claim-vs-evidence table, replay/probe notes, verdict, acceptance section |

Trail home:

```text
docs/governance/cecp/trails/<trail-id>/
  README.md                 # lineage index + status summary
  01-architect-adr.md
  02-builder-scaffold-manifest.md
  03-implementor-notes.md
  04-reviewer-conformance.md
  05-inspector-acceptance.md
  lineage.json              # optional machine-readable handoff (see schema)
```

Reusable templates: `docs/governance/cecp/EVIDENCE_TRAIL_TEMPLATE.md`,
`docs/governance/cecp/lineage.schema.json`.

Reference implementations (registry): see **§9** below. Layer stack context:
`docs/governance/CONSTITUTIONAL_LAYER_STACK.md` (CECP / CHEA / CCR / CDGF).

## 4. Handoff / lineage schema

Logical chain:

```text
Architecture → Build → Implementation → Review → Inspection → Acceptance
```

Each stage record SHOULD include:

| Field | Description |
|-------|-------------|
| `trailId` | Stable id (directory name), e.g. `prompt-scene-adapter-2026-07` |
| `stage` | `architect` \| `builder` \| `implementor` \| `reviewer` \| `inspector` \| `acceptance` |
| `predecessor` | Prior stage id or null for Architect |
| `intent` | Declared purpose (P1) |
| `artifacts` | Paths written or cited this stage |
| `evidence` | Tests, commands, file citations |
| `statusTags` | Map of claim → tag |
| `handoff` | What the next role must do |
| `verdict` | Inspector only: `PASS` \| `PASS_WITH_GAPS` \| `FAIL` |

Machine shape: see `docs/governance/cecp/lineage.schema.json`.

### 4.1 PASS_WITH_GAPS is intended constitutional behavior

`PASS_WITH_GAPS` is **not** a soft failure. It is the preferred Inspector outcome when:

1. Core acceptance criteria for the trail are met with cited probes, **and**
2. Remaining gaps are listed explicitly with status tags and a promotion path.

Prefer accumulating evidence-backed CECP references (and closing gaps in later trails)
over one-off “green” features that hide incompleteness. Promote gaps only when new
tests/code evidence justify a stronger tag (Drive-G-1).

## 5. Status tags

Use only these four (MRS / Drive-G-1):

| Tag | Meaning |
|-----|---------|
| **enforced** | Implementation + tests (or CI) prove the claim |
| **partial** | Some paths work / some tests pass; gaps listed |
| **declared** | Designed or roadmap; not implemented here |
| **skeleton** | Stub / identity / placeholder only |

Do not use “production ready” without naming **which maturity dimension** and audience (Drive-G-2).

## 6. Explicit non-goals

CECP Ω∞ does **not**:

- Replace the product / project **maturity scorecard** (`docs/scorecards/…`, Drive-G-2)
- Auto-amend `constitution/CHARTER.md`, `engine/constitution/*`, `AGENTS.md`, or `default.policies.json`
- Imply cross-org runtime gates (Research OS, PARAGON One, Sovereign X OS, CIEMS, DAR-Z)
- Guarantee that chat-only crew runs are complete — **trail files are the completion criterion**
- Substitute for the 16 MRS conformance checks on constitutional engine subsystems

## 7. MRS crew skills ↔ CECP stages

| CECP stage | Cursor skill | OpenCode agent | Protocol duty |
|------------|--------------|----------------|---------------|
| Architect | `mrs-architect` | `.opencode/agents/architect.md` | Write `01-architect-adr.md` into the trail |
| Builder | `mrs-builder` | `.opencode/agents/builder.md` | Write `02-builder-scaffold-manifest.md` |
| Implementor | `mrs-implementor` | `.opencode/agents/implementor.md` | Write `03-implementor-notes.md` |
| Reviewer | `mrs-reviewer` | `.opencode/agents/reviewer.md` | Write `04-reviewer-conformance.md` (read-only product code; trail write is allowed for evidence) |
| Inspector | `mrs-inspector` | `.opencode/agents/inspector.md` | Write `05-inspector-acceptance.md` |
| Foreman | `mrs-crew` | — | Create trail dir; require stage files; merge handoffs |

**Foreman rule:** after each role returns, ensure the corresponding trail file exists under
`docs/governance/cecp/trails/<id>/` before starting the next stage. Full protocol text lives
here; skills keep one-line pointers (progressive disclosure).

**Read-only roles vs trail writes:** Architect / Reviewer / Inspector remain banned from
product/source edits; writing CECP trail markdown under `docs/governance/cecp/trails/` is
part of the protocol and is the permanent evidence channel (foreman may write trails from
role returns if a subagent cannot write).

## 8. Cross-project adoption (**declared**)

The following orgs/products may adopt CECP Ω∞ later. Until each has its own trail home,
skills, and evidence, treat this section as **declared** roadmap only:

| Project / OS | Adoption status |
|--------------|-----------------|
| Mandala Rendering Software (MRS) | **partial** (this document + skills + reference trails) |
| Research OS | **declared** |
| PARAGON One | **declared** |
| Sovereign X OS | **declared** |
| CIEMS | **declared** |
| DAR-Z | **declared** |

Do not claim “CECP enforced across Drive G” without per-repo artifacts.

## 9. Reference implementations registry

CECP Ω∞ prefers **accumulating governed references** (full five-stage trails + honest
tags) over one-off features. Registry below is evidence-bound (Drive-G-1).

| # | Reference | Trail | SoT / contract | Inspector | Notes |
|---|-----------|-------|----------------|-----------|-------|
| **1** | Prompt→Scene adapter | `docs/governance/cecp/trails/prompt-scene-adapter-2026-07/` | `mrs/adapters/prompt-scene-bridge/` · `CONTRACT.md` | **PASS_WITH_GAPS** | First CECP Ω∞ reference. Mapping + Genblaze HTTP **enforced**; contemporaneous expand stub **skeleton** (see follow-ons). |
| 1a | Engine3D world expand (follow-on) | `docs/governance/cecp/trails/engine3d-expand-2026-07/` | `engine3d-core` expand CLI + bridge opt-in | **PASS** | Closes empty-world gap from #1 for star/mandala when Node/`dist` present; default stub still **partial**. |
| 1b | Prompt→Scene Docker wiring (follow-on) | `docs/governance/cecp/trails/prompt-scene-docker-2026-07/` | repo-root `Dockerfile` + Genblaze `/app` layout | **PASS_WITH_GAPS** | Operator image path; live daemon/Render gaps listed. |
| **2** | Prompt→Scene→4D-ProtonRaster (six mods) | `docs/governance/cecp/trails/proton-raster-2026-07/` | `mrs/packages/renderer-core/src/render/rt4d/proton/` · `mrs/adapters/proton-raster-bridge/CONTRACT.md` | **PASS_WITH_GAPS** | Second CECP Ω∞ reference. Six CPU mods + PNG **enforced**; Genblaze host **partial**; anisotropic/GPU/roadmap mods **declared**. Landmark commit: `8fa2bc3`. |

**Promotion rule:** a new feature becomes a numbered reference only when it has a
complete trail (01–05 + README), claim↔evidence rows, and an Inspector verdict.
Gaps stay tagged until a follow-on trail promotes them.

Layer framing (how CECP relates to CHEA / CCR / CDGF):  
`docs/governance/CONSTITUTIONAL_LAYER_STACK.md`.

---

> “No action without evidence. No claim without proof. No system without governance.”
> — Constitutional Engine Charter v1.0 (cited; not amended by this protocol)
