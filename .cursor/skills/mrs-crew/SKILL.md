---
name: mrs-crew
description: >-
  Orchestrates the local MRS six-role crew (architect, builder, implementor,
  reviewer, inspector, ESFR / engineer-standards). Use when the user asks to use
  the crew, subagents, or to design→build→implement→review→inspect→standards /
  ESFR a feature instead of doing all roles in one pass. Optional crew modes
  (Sage…Visionary, 20 lenses) are flavors on roles — not new pipeline stages.
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

**Optional crew modes** (lenses on any role): see
`docs/governance/cecp/CREW_MODES.md` and `.cursor/skills/mrs-crew/SAGE.md`.
Modes are **not** new stages or agents. Status: **partial**.

ESFR package: `docs/governance/esfr/`. ESFR **is** stage-06 Engineer Standards —
not a parallel seventh role.

## Default pipeline (CECP Ω∞)

Protocol: `docs/governance/CECP_OMEGA_PROTOCOL.md`  
Template: `docs/governance/cecp/EVIDENCE_TRAIL_TEMPLATE.md`  
ESFR: `docs/governance/esfr/protocol.esfr.md`  
Modes suite: `docs/governance/cecp/CREW_MODES.md`  
Sage detail: `docs/governance/cecp/SAGE_MODE.md`

1. **Architect** → `01-architect-adr.md`
2. **Builder** → `02-builder-scaffold-manifest.md`
3. **Implementor** → `03-implementor-notes.md`
4. **Reviewer** → `04-reviewer-conformance.md`
5. **Inspector** → `05-inspector-acceptance.md`
6. **ESFR** → `06-engineer-standards.md`;
   PromotionEligibility: PROMOTE / PROMOTE_WITH_GAPS / HOLD / REJECT  

Any stage may add an optional **mode lens** from the 20-mode suite in
`docs/governance/cecp/CREW_MODES.md` (Sage…Bard + Oracle…Visionary) without
changing order.

**Permanent trail (required):** before finishing the crew run, ensure
`docs/governance/cecp/trails/<trail-id>/` exists with the six stage files (+
`README.md`). Historical trails that stop at 05 remain valid; **new** trails
must include ESFR (06). If a read-only subagent cannot write, the foreman writes the
trail from that role’s return. Skip roles only when the user explicitly narrows
scope.

Reference registry: `docs/governance/CECP_OMEGA_PROTOCOL.md` §9
(#1 Prompt→Scene, #2 Proton Raster; follow-ons listed there).
Layer stack: `docs/governance/CONSTITUTIONAL_LAYER_STACK.md`.

## Crew modes (optional lenses)

**Precedence:** base role hard bans > Sage rigor > mode lens.
**Roster:** 20 modes — full index `docs/governance/cecp/CREW_MODES.md`.

| Mode | One-line |
|------|----------|
| Sage | Elevated rigor, §9, anti-overclaim |
| Trickster | Constructive adversarial edges |
| Warrior | Minimal scope, ship-gate focus |
| Monk | Calm simplicity, quiet determinism |
| Researcher | Cite evidence; hypothesis→tests |
| Journalist | Who/what/when/evidence voice |
| Poet | Honest metaphor; no capability fiction |
| Physicist | Units, conservation, RT4D math |
| Theorist | Invariants, formal design properties |
| Bard | Judge-facing narrative without false claims |
| Oracle | Long-horizon foresight (declared risks) |
| Cartographer | System/trail/pipeline maps |
| Artisan | Pixel/tonemap/beauty craft |
| Sentinel | Guard determinism & boundaries |
| Scholar | Docs/contracts/evidence mastery |
| Inventor | Novel mechanisms; dual-tag declared vs shipped |
| Diplomat | Multi-party coherence; honest layer tags |
| Hermit | Deeper purity/withdrawal (≠ Monk) |
| Historian | Lineage/archival continuity |
| Visionary | Bold leaps + mandatory anti-overclaim |

**Invoke:** “\<Mode\> \<Role\>” (e.g. Artisan Architect), “\<Mode\> mode”, or
foreman picks per stage. Compose: “Sage + Cartographer”.

When mode selected: load `CREW_MODES.md`; if Sage, also `SAGE_MODE.md`; remind
bans; record `lens:` / `mode: sage` on trail.

## How to dispatch (Cursor)

For each role, launch a `Task` (`generalPurpose` or `explore` for read-only):

1. Read that role’s skill `SKILL.md` (or OpenCode agent `.md`)
2. Put the full role instructions in the Task prompt under **Role law**
3. Attach the prior role’s artifact (Architect plan → Builder, etc.)
4. Require the role’s **Output** format in the return
5. If mode/Sage: name it, attach `CREW_MODES.md` (+ `SAGE_MODE.md` if Sage)

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
