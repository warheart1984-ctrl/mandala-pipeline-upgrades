---
name: mrs-crew
description: >-
  Orchestrates the local MRS six-role crew (architect, builder, implementor,
  reviewer, inspector, engineer-standards). Use when the user asks to use the
  crew, subagents, or to design→build→implement→review→inspect→standards a
  feature instead of doing all roles in one pass.
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
| Engineer Standards | `.opencode/agents/engineer-standards.md` | `mrs-engineer-standards` | No |

## Default pipeline (CECP Ω∞)

Protocol: `docs/governance/CECP_OMEGA_PROTOCOL.md`  
Template: `docs/governance/cecp/EVIDENCE_TRAIL_TEMPLATE.md`

1. **Architect** — plan + file manifest + acceptance tests → trail `01-architect-adr.md`  
2. **Builder** — scaffolds from manifest → `02-builder-scaffold-manifest.md`  
3. **Implementor** — real logic + tests green → `03-implementor-notes.md`  
4. **Reviewer** — constitutional / defect review (read-only product code) → `04-reviewer-conformance.md`  
5. **Inspector** — run probes; PASS / PASS_WITH_GAPS / FAIL → `05-inspector-acceptance.md`  
6. **Engineer Standards** — final ship gate (coding / API / claims / CI / ops / license); PASS / PASS_WITH_NOTES / FAIL → `06-engineer-standards.md`  

**Permanent trail (required):** before finishing the crew run, ensure
`docs/governance/cecp/trails/<trail-id>/` exists with the six stage files (+
`README.md`). Historical trails that stop at 05 remain valid; **new** trails
should include 06. If a read-only subagent cannot write, the foreman writes the
trail from that role’s return. Skip roles only when the user explicitly narrows
scope.

Reference registry: `docs/governance/CECP_OMEGA_PROTOCOL.md` §9
(#1 Prompt→Scene, #2 Proton Raster; follow-ons listed there).
Layer stack: `docs/governance/CONSTITUTIONAL_LAYER_STACK.md`.

## How to dispatch (Cursor)

For each role, launch a `Task` (`generalPurpose` or `explore` for read-only):

1. Read that role’s skill `SKILL.md` (or OpenCode agent `.md`)
2. Put the full role instructions in the Task prompt under **Role law**
3. Attach the prior role’s artifact (Architect plan → Builder, etc.)
4. Require the role’s **Output** format in the return

Read-only roles (Architect, Reviewer, Inspector, Engineer Standards): prefer explore / insist no file writes.  
Write roles (Builder, Implementor): generalPurpose; remind protected paths.

## Your job as foreman

- Give short orders; do not re-implement what a role just did
- Merge handoffs into one status line for the user
- Create/update the CECP trail dir; block “done” until stage artifacts exist
- If Inspector FAILs → send gaps back to Implementor once, then Inspector again
- If Engineer Standards FAILs → send gaps to Implementor (or docs), then re-run Standards
- Do not declare ship-ready until Engineer Standards returns PASS or PASS_WITH_NOTES
- Never modify constitutional protected paths (`constitution/`, `engine/constitution/`,
  `AGENTS.md`, `default.policies.json`, …) without explicit user auth — CECP trails
  under `docs/governance/cecp/` are allowed
