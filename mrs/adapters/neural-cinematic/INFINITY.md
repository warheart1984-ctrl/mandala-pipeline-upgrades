# Infinity / Story Forge on this machine

**Root:** `/media/jon/New Volume/Project Infinity` (clone of `warheart1984-ctrl/infinity`)  
**Story Forge:** `external/story_forge`  
**Beatbox:** `external/beatbox_speakers`

Override with `INFINITY_ROOT`.

## Mandala boundary

Mandala does **not** host Movie Lane. It maps Infinity-shaped JSON via
`mrs/adapters/storyforge-boundary` (`storyforge-mandala-contract/1.1`).

```bash
export INFINITY_ROOT="/media/jon/New Volume/Project Infinity"
cd mrs/adapters/neural-cinematic
python3 infinity_bridge.py
```

## Honest status

| Piece | Status |
|-------|--------|
| Infinity clone present | **partial** (on volume) |
| Warrior fixture → Mandala map | **partial** (parity in `infinity_bridge.parity_report`) |
| Live `BackendBuildArtifact.to_payload()` | **partial_with_gaps** — Infinity's native payload is thinner than the Mandala warrior fixture; operators export enriched JSON or use the fixture until Movie Lane emit is wired |
| Movie Lane book→shots | **declared** on Infinity; Mandala `book_drop.py` is a **bridge heuristic** for Ch1 demos only |

Do not invent narrative identity in Mandala. Pass `identityLock` from Story Forge.
