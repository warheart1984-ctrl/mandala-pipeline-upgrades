---
name: mrs-crew
description: >-
  Orchestrates the local MRS six-role crew (architect, builder, implementor,
  reviewer, inspector, ESFR / engineer-standards). Use when the user asks to use
  the crew, subagents, or to design→build→implement→review→inspect→standards /
  ESFR a feature instead of doing all roles in one pass. Optional Sage mode
  elevates rigor per role without adding pipeline stages.
---

# MRS Crew Orchestrator

You are the **foreman**. Prefer dispatching role work over doing every role yourself.

## Roles (local)

| Role | OpenCode agent | Cursor skill | Writes code? |
|------|----------------|--------------|--------------|
| Architect | `.opencode/agents/architect.md` | `mrs-architect` | No |
| Builder | `.opencode/agents/builder.md` | `mrs-builder` | Stubs only |
| Implementor | `.opencode/agents/implementor.md` | `mrs-implementor` | Yes |
| Reviewer | `.opencode/agents/reviewer.md` | `mrs-reviewer` | No |
| Inspector | `.opencode/agents/inspector.md` | `mrs-inspector` | No |
| **ESFR** (Engineer Standards) | `.opencode/agents/engineer-standards.md` | `mrs-engineer-standards` | No |

Each role supports optional **Sage mode** (same agent/skill +
`docs/governance/cecp/SAGE_MODE.md`) — elevated rigor of **that** role only.
Sage is **not** a seventh stage. See `.cursor/skills/mrs-crew/SAGE.md`.

ESFR package: `docs/governance/esfr/`. ESFR **is** stage-06 Engineer Standards —
not a parallel seventh role.

## Default pipeline (CECP Ω∞)

Protocol: `docs/governance/CECP_OMEGA_PROTOCOL.md`  
Template: `docs/governance/cecp/EVIDENCE_TRAIL_TEMPLATE.md`  
ESFR: `docs/governance/esfr/protocol.esfr.md`  
Sage (optional per stage): `docs/governance/cecp/SAGE_MODE.md`

1. **Architect** → `01-architect-adr.md` (optional Architect Sage)
2. **Builder** → `02-builder-scaffold-manifest.md` (optional Builder Sage)
3. **Implementor** → `03-implementor-notes.md` (optional Implementor Sage)
4. **Reviewer** → `04-reviewer-conformance.md` (optional Reviewer Sage)
5. **Inspector** → `05-inspector-acceptance.md` (optional Inspector Sage)
6. **ESFR** → `06-engineer-standards.md` (optional ESFR Sage);
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

## Sage mode (any role)

Sage elevates depth of the **current** role. It does **not** reorder the
pipeline or let a role steal another role’s job. Hard bans unchanged.
Capability: **partial**.

| Invoke | Phrases |
|--------|---------|
| Architect Sage | “Sage mode”, “Architect Sage” |
| Builder Sage | “Builder Sage”, “sage builder” |
| Implementor Sage | “Implementor Sage” |
| Reviewer Sage | “Reviewer Sage” |
| Inspector Sage | “Inspector Sage” |
| ESFR Sage | “ESFR Sage”, “Engineer Standards Sage” |

Foreman may also select Sage for a stage on hard/cross-domain work.

**When Sage:** load `docs/governance/cecp/SAGE_MODE.md` (+ role `SAGE.md` if any);
require Anti-overclaim, Sage counsel, Cross-reference ledger; mark trail
`mode: sage`.

| Prefer Sage | Prefer default |
|-------------|----------------|
| User asked for Sage / \<Role\> Sage | Routine single-domain stage |
| Cross-domain or promotion-critical | Narrow acceptance already clear |
| Prior stage left coherence gaps | Time-boxed stub fill |

## How to dispatch (Cursor)

For each role, launch a `Task` (`generalPurpose` or `explore` for read-only):

1. Read that role’s skill `SKILL.md` (or OpenCode agent `.md`)
2. Put the full role instructions in the Task prompt under **Role law**
3. Attach the prior role’s artifact (Architect plan → Builder, etc.)
4. Require the role’s **Output** format in the return
5. If Sage: name “\<Role\> Sage”, attach `SAGE_MODE.md`, require Sage sections

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
