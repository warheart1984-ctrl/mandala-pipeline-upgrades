# 06 — Engineer Standards (ESFR)

| Field | Value |
| --- | --- |
| `mode` | Anchor |
| `cognitive-profile` | Guardian + Steward |
| `softwareCreationMode` | Runtime-Sage |
| ESFRVerdict | **PASS_WITH_GAPS** |
| PromotionEligibility | **PROMOTE_WITH_GAPS** |

## Test matrix

| Suite | Command | Result |
| --- | --- | --- |
| Continuity | `test:projection` (continuity) | PASS |
| Invariants | `test:projection` (invariants) | PASS |
| Lens verifier | `test:projection` (northstar) | PASS (incl. soft_skip) |
| Aggregate | 20 tests | **20 pass / 0 fail** |

## Probes (01–08 style)

| Probe | Citation | Result |
| --- | --- | --- |
| 01 Intent declared | PCC preamble + ADR | PASS |
| 02 SoT not duplicated | projector.js still closed form | PASS |
| 03 Status tags honest | no enforced in PCC_INVARIANTS | PASS |
| 04 Continuity evidence | continuity tests | PASS |
| 05 Print sovereignty | aperture role ≠ print_sot | PASS |
| 06 Lens hooks | HyperCausticLensVerifier | PASS_WITH_GAPS |
| 07 Path-tracer honesty | wired=false | PASS |
| 08 GPU assist-only | INTEGRATION_NOTES / PCC §8 | PASS (docs) |

## Capability tags summary

| Capability | Tag |
| --- | --- |
| ProjCC contract docs | **declared** (ratified-as-declared) |
| ProjectionState / Kernel / continuous P | **partial** |
| Observation presets (core PLP) | **partial** |
| Orbit / soft_caustic presets | **declared** |
| ApertureFrame3D API | **partial** |
| Hyper-Caustic verifier hooks | **declared** |
| Lens north-star visual | **declared** / soft_skip |
| Path-tracer bind | **declared** |
| CKL / enforced gate | **not claimed** |

## PromotionEligibility

**PROMOTE_WITH_GAPS** — mergeable as partial continuity layer; gaps listed in README.
Not eligible for bare “production ready observation engine” claims (Drive-G-2).

## ESFRVerdict

**PASS_WITH_GAPS**
