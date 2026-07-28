# CECP Evidence Trail Template

Copy this folder pattern to:

```text
docs/governance/cecp/trails/<trail-id>/
```

Fill every section with paths and commands. Prefer weaker verbs when evidence is incomplete (Drive-G-1).

**New trails** must include stage 06. Historical trails that closed at 05 are not rewritten.

---

## Trail metadata

| Field | Value |
|-------|-------|
| `trailId` | |
| `feature` | |
| `requestedBy` | |
| `started` | YYYY-MM-DD |
| `lineage` | Architecture → Build → Implementation → Review → Inspection → Standards Acceptance |
| `overallStatus` | **partial** / **enforced** / **declared** (pick one; justify) |
| `protocol` | `docs/governance/CECP_OMEGA_PROTOCOL.md` |

---

## Stage checklist

- [ ] `01-architect-adr.md`
- [ ] `02-builder-scaffold-manifest.md`
- [ ] `03-implementor-notes.md`
- [ ] `04-reviewer-conformance.md`
- [ ] `05-inspector-acceptance.md`
- [ ] `06-engineer-standards.md` (required for new trails)
- [ ] `lineage.json` (optional)
- [ ] `README.md` (index)

---

## 01 — Architect (ADR + boundary)

**File:** `01-architect-adr.md`

Required headings:

1. Intent (what / why)
2. ADR decision (context, decision, consequences)
3. Interface specification (inputs, outputs, schemas, env, bans)
4. Constitutional boundary analysis (in-scope / out-of-scope / protected paths)
5. File manifest (path × action × owner role)
6. Acceptance criteria (testable)
7. Handoff to Builder

---

## 02 — Builder (scaffold)

**File:** `02-builder-scaffold-manifest.md`

Required headings:

1. Intent (cite Architect ADR)
2. Scaffold manifest (created paths)
3. Dependency graph (modules / packages / subprocess boundaries)
4. Build artifacts inventory (stubs labeled **skeleton** / **declared**)
5. Test placeholders created
6. Handoff to Implementor

---

## 03 — Implementor (production notes)

**File:** `03-implementor-notes.md`

Required headings:

1. Intent fulfilled
2. Files touched (real paths)
3. Unit / integration test inventory (names + what they enforce — do not invent counts)
4. Commands run + results
5. Status tag updates
6. Remaining gaps
7. Handoff to Reviewer

---

## 04 — Reviewer (conformance)

**File:** `04-reviewer-conformance.md`

Required headings:

1. Scope reviewed
2. Principles P1–P5 findings
3. Policy / ban / boundary findings
4. Constitutional / contract findings (lawbook focus; leave ship-quality to stage 06)
5. Violations (or “none found” with evidence)
6. Boundary verdict (e.g. Boundary OK)
7. Handoff to Inspector

---

## 05 — Inspector (acceptance)

**File:** `05-inspector-acceptance.md`

Required headings:

1. Verdict: `PASS` | `PASS_WITH_GAPS` | `FAIL`
2. Claim ↔ evidence table
3. Commands / probes run
4. Replay / determinism notes (if applicable)
5. Gaps for Implementor
6. Claim wording to downgrade (if any)
7. **Acceptance** — accepted / rejected as governed integration point; list gaps honestly
8. Handoff to Engineer Standards (new trails)

---

## 06 — Engineer Standards (ship gate)

**File:** `06-engineer-standards.md`

Required headings:

1. Verdict: `PASS` | `PASS_WITH_NOTES` | `FAIL`
2. Standards checklist (coding/API, Drive-G-1, Drive-G-2, CI/tests, Docker/ops notes, deps/license, no drive-by scope)
3. Findings (blocking vs notes)
4. Ship gate decision (ready / blocked / ship with notes)
5. Distinct from Reviewer — do not re-litigate P1–P5 unless a standards finding depends on it

---

## Acceptance block (canonical)

```markdown
## Acceptance

**Decision:** Accepted as governed integration point with gaps | Rejected | Deferred

**Enforced today:** …
**Partial / skeleton gaps:** …
**Declared non-goals:** …
**Standards Acceptance (stage 06):** PASS | PASS_WITH_NOTES | FAIL | N/A (historical trail)
```
