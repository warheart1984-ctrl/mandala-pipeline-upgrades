---
name: mrs-crew
description: >-
  Orchestrates the local MRS six-role crew (architect, builder, implementor,
  reviewer, inspector, ESFR / engineer-standards). Use when the user asks to use
  the crew, subagents, or to design→build→implement→review→inspect→standards /
  ESFR a feature instead of doing all roles in one pass.
---

# MRS Crew Orchestrator

You are the **foreman**. Prefer dispatching role work over doing every role yourself.

## Roles (local)

| Role | OpenCode agent | Cursor skill | Writes code? |
|------|----------------|--------------|--------------|
| Architect | `.opencode/agents/architect.md` | `mrs-architect` | No |
| Architect Sage | same agent/skill, **Sage mode** | `mrs-architect` + `SAGE.md` | No (design-only elevation — **not** a seventh stage) |
| Builder | `.opencode/agents/builder.md` | `mrs-builder` | Stubs only |
| Implementor | `.opencode/agents/implementor.md` | `mrs-implementor` | Yes |
| Reviewer | `.opencode/agents/reviewer.md` | `mrs-reviewer` | No |
| Inspector | `.opencode/agents/inspector.md` | `mrs-inspector` | No |
| **ESFR** (Engineer Standards Final Reviewer) | `.opencode/agents/engineer-standards.md` | `mrs-engineer-standards` | No |

ESFR package: `docs/governance/esfr/`. ESFR **is** stage-06 Engineer Standards —
not a parallel seventh role.

## Default pipeline (CECP Ω∞)

Protocol: `docs/governance/CECP_OMEGA_PROTOCOL.md`  
Template: `docs/governance/cecp/EVIDENCE_TRAIL_TEMPLATE.md`  
ESFR: `docs/governance/esfr/protocol.esfr.md`

1. **Architect** — plan + file manifest + acceptance tests → trail `01-architect-adr.md`  
   (optional **Architect Sage** / Sage mode — same stage 01; see below)  
2. **Builder** — scaffolds from manifest → `02-builder-scaffold-manifest.md`  
3. **Implementor** — real logic + tests green → `03-implementor-notes.md`  
4. **Reviewer** — constitutional / defect review (read-only product code) → `04-reviewer-conformance.md`  
5. **Inspector** — run probes; PASS / PASS_WITH_GAPS / FAIL → `05-inspector-acceptance.md`  
6. **ESFR** — final ship gate; run `test-matrix.esfr.md` + `probes.esfr.md`;
   PASS / PASS_WITH_GAPS / HOLD / REJECT → `06-engineer-standards.md`;
   PromotionEligibility: PROMOTE / PROMOTE_WITH_GAPS / HOLD / REJECT  

**Permanent trail (required):** before finishing the crew run, ensure
`docs/governance/cecp/trails/<trail-id>/` exists with the six stage files (+
`README.md`). Historical trails that stop at 05 remain valid; **new** trails
must include ESFR (06). If a read-only subagent cannot write, the foreman writes the
trail from that role’s return. Skip roles only when the user explicitly narrows
scope.

Reference registry: `docs/governance/CECP_OMEGA_PROTOCOL.md` §9
(#1 Prompt→Scene, #2 Proton Raster; follow-ons listed there).
Layer stack: `docs/governance/CONSTITUTIONAL_LAYER_STACK.md`.

## Architect vs Architect Sage

Sage is a **mode of Architect** (stage 01), not a new crew stage and not ESFR.

| Invoke | When |
|--------|------|
| **Default Architect** | Single-domain or routine plans; clear ADR scope; user did not ask for Sage |
| **Architect Sage** | User says “Sage mode” / “Architect Sage”; **or** hard cross-domain design (Prompt→Scene × Engine3D × RT4D/Proton × Genblaze); **or** promotion/ESFR implications need layer + §9 coherence up front |

When invoking Sage: load `mrs-architect/SKILL.md` **and** `mrs-architect/SAGE.md`;
require extra sections (`Anti-overclaim`, `Sage counsel`, `Cross-reference ledger`,
`Risks to sovereignty / determinism`); mark trail `01` metadata `mode: sage`.
Capability is **partial** / skill-declared — not CHEA/CCR/CDGF enforcement.

## How to dispatch (Cursor)

For each role, launch a `Task` (`generalPurpose` or `explore` for read-only):

1. Read that role’s skill `SKILL.md` (or OpenCode agent `.md`)
2. Put the full role instructions in the Task prompt under **Role law**
3. Attach the prior role’s artifact (Architect plan → Builder, etc.)
4. Require the role’s **Output** format in the return

For **Architect Sage**: same as Architect, plus instruct Sage mode triggers and
extra output sections from `SAGE.md`.

For **ESFR** specifically: attach Inspector verdict + module paths + trail id;
require `ESFRVerdict`, full test-matrix table, probes 01–08 citations, and
`PromotionEligibility` (`PROMOTE` | `PROMOTE_WITH_GAPS` | `HOLD` | `REJECT`).
Do **not** fabricate PASS / PROMOTE on an unfinished crew.

Read-only roles (Architect, Reviewer, Inspector, ESFR): prefer explore / insist no file writes.  
Write roles (Builder, Implementor): generalPurpose; remind protected paths.

## Your job as foreman

- Give short orders; do not re-implement what a role just did
- Merge handoffs into one status line for the user
- Create/update the CECP trail dir; block “done” until stage artifacts exist
- If Inspector FAILs → send gaps back to Implementor once, then Inspector again
- If ESFR returns HOLD or REJECT → send gaps to Implementor (or docs), then re-run ESFR
- Do not declare ship-ready / promotion-eligible until ESFR returns PASS or
  PASS_WITH_GAPS with PromotionEligibility `PROMOTE` or `PROMOTE_WITH_GAPS`
- Never modify constitutional protected paths (`constitution/`, `engine/constitution/`,
  `AGENTS.md`, `default.policies.json`, …) without explicit user auth — CECP trails
  under `docs/governance/cecp/` and ESFR docs under `docs/governance/esfr/` are allowed
