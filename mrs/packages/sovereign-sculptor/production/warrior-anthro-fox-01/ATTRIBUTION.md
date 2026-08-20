# Attribution — warrior-anthro-fox-01 production mesh

## Honest status

This is a **downloaded free mesh for pipeline test**, **not** a custom ZBrush
hero sculpt by the project owner. It unlocks `productionSculpt=true` so the
neural-cinematic / identityLock intake path can be exercised end-to-end.

Status tag for this drop: **`partial_with_gaps`**

## Source

| Field | Value |
|-------|--------|
| Title | Low Poly Fox |
| Author | Mathilde_Lea |
| URL | https://opengameart.org/content/low-poly-fox |
| License | [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| Original file | `Fox/Fox1.fbx` inside `fox.zip` |
| Local file | `sculpt.fbx` (verbatim copy of `Fox1.fbx`) |
| Downloaded | 2026-08-20 |

## Species / identity mismatch (documented)

- Character id remains **`warrior-anthro-fox-01`**.
- `identityLock.species` remains **`anthro-fox`** (do not rewrite to claim this mesh is anthro).
- Mesh reality: **quadruped low-poly fox** (game asset), **not** an anthropomorphic / furry warrior, and **not** a ZBrush production hero.
- Prefer anthro fox / warrior when a free CC0/CC-BY anthro becomes available; until then this fox stand-in is intentional for intake hashing + demo wiring.

## Changes from upstream

- Renamed `Fox1.fbx` → `sculpt.fbx` for Mandala ZBrush intake naming.
- Optional local texture copy: `Fox_Base_Color.png` (from upstream `Fox Base Color.png`; `*.png` is gitignored — keep beside mesh for bake reference only).
- No remesh / decimation (already tiny ~49 KiB).

## Credit line (CC-BY)

> Low Poly Fox by Mathilde_Lea (OpenGameArt), licensed under CC-BY 4.0.
> https://opengameart.org/content/low-poly-fox

## Intake evidence (2026-08-20)

- `productionSculpt`: **true** after `sculpt_under_lock.resolve_sculpt_under_lock`
- `meshHash`: `sha256:86240c1c98709300a04054266ed3308a20d53828c3953b56cac2123d7206db5a`
- Demo: `bash mrs/adapters/neural-cinematic/demo-live-sf.sh` → `provenance.sculpt.productionSculpt=True`
