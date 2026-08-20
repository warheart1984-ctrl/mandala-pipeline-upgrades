#!/usr/bin/env python3
"""Live Story Forge emit → Mandala-ready --build-json.

Runs Infinity `StoryForgeBackendPipeline`, then enriches the thin `to_payload()`
with narrative_state (including identityLock), temporal_shot_list, and worldPack
so `map_infinity.from_infinity_backend_build` accepts it.

Status: **partial_with_gaps**
- Live SF shot list: yes (when Infinity import works)
- identityLock: operator-supplied (Story Forge does not invent a Story Bible)
- audioPlan: synthesized by Mandala mapper if omitted
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from infinity_bridge import find_infinity_root, map_build_to_mandala, story_forge_src  # noqa: E402


def _dc(obj: Any) -> Any:
    if is_dataclass(obj):
        return {k: _dc(v) for k, v in asdict(obj).items()}
    if isinstance(obj, (list, tuple)):
        return [_dc(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _dc(v) for k, v in obj.items()}
    return obj


def _default_warrior_sculpt() -> dict[str, Any]:
    """Resolve warrior sculpt under lock (production OBJ preferred; else fixture)."""
    from sculpt_under_lock import resolve_sculpt_under_lock

    return resolve_sculpt_under_lock("warrior-anthro-fox-01")


def _default_warrior_lock() -> dict[str, Any]:
    return _default_warrior_sculpt()["identityLock"]


def enrich_for_mandala(
    artifact: Any,
    *,
    character_id: str,
    identity_lock: dict[str, Any],
    display_name: str,
    world_pack: dict[str, Any] | None = None,
) -> dict[str, Any]:
    thin = dict(artifact.to_payload())
    ns = _dc(artifact.narrative_state)
    # Attach identityLock — SF characters are name/role/description only.
    chars_in = list(ns.get("characters") or [])
    if not chars_in:
        chars_in = [{"name": display_name, "role": "hero", "description": display_name}]
    chars_out = []
    for i, c in enumerate(chars_in):
        entry = dict(c) if isinstance(c, dict) else {"name": str(c)}
        if i == 0:
            entry["characterId"] = character_id
            entry["identityLock"] = identity_lock
            entry.setdefault("name", display_name)
        chars_out.append(entry)
    ns["characters"] = chars_out

    temporal = _dc(artifact.temporal_shot_list)
    # Ensure shotId / pose fields Mandala mapper expects
    shots = []
    for i, s in enumerate(temporal.get("shots") or []):
        shot = dict(s)
        n = int(shot.get("shot_number") or i + 1)
        shot.setdefault("shotId", f"S{n:02d}")
        shot.setdefault("pose", shot.get("action") or f"pose-{n}")
        shots.append(shot)
    temporal["shots"] = shots

    payload = {
        **thin,
        "narrative_state": ns,
        "temporal_shot_list": temporal,
        "worldPack": world_pack
        or {
            "id": f"world-{thin.get('scene_id') or 'sf-live'}",
            "setting": str(ns.get("setting") or "storyforge-live"),
            "weather": "unspecified",
            "lighting": "unspecified",
            "notes": "Enriched from live StoryForgeBackendPipeline for Mandala intake",
        },
        "continuityConstraints": {
            "sameCharacterAcrossShots": True,
            "persistentEquipment": True,
            "persistentWorld": True,
        },
        "renderIntent": {
            "summary": "storyforge-live-emit",
            "route": "rt4d",
            "quality": "draft",
        },
        "provenance": {
            "source": "story_forge.StoryForgeBackendPipeline",
            "statusTag": "partial_with_gaps",
            "infinityRepo": "warheart1984-ctrl/infinity",
            "limitation": (
                "Live SF shots + operator identityLock. Thin to_payload alone is not Mandala-ready; "
                "this file is the enriched handoff."
            ),
            "emittedAt": datetime.now(timezone.utc).isoformat(),
            "sculpt": {
                "characterId": character_id,
                # Honest flag filled by emit_live_build after sculpt resolve
                "productionSculpt": False,
            },
        },
    }
    return payload


def emit_live_build(
    *,
    prompt: str,
    setting: str,
    tone: str,
    key_moments: list[str],
    character_id: str,
    identity_lock: dict[str, Any],
    display_name: str,
    session_id: str,
    out_json: Path,
    output_root: Path | None = None,
) -> dict[str, Any]:
    src = story_forge_src()
    if not src:
        raise SystemExit(
            "Infinity/Story Forge not found. Set INFINITY_ROOT or clone to "
            "'/media/jon/New Volume/Project Infinity'"
        )
    sys.path.insert(0, str(src))
    from story_forge.backend_full_build import NarrativeState, StoryForgeBackendPipeline

    root = find_infinity_root()
    out_root = output_root or (ROOT / "outputs" / "storyforge-builds")
    out_root.mkdir(parents=True, exist_ok=True)

    pipeline = StoryForgeBackendPipeline(output_root=out_root)
    narrative = NarrativeState(
        prompt=prompt,
        characters=[
            {
                "name": display_name,
                "role": "hero",
                "description": f"{character_id} under identityLock",
            }
        ],
        setting=setting,
        tone=tone,
        key_moments=key_moments or ["Opening", "Middle", "Close"],
    )
    artifact = pipeline.run(
        session_id=session_id,
        narrative_state=narrative,
        target="movie",
        source_mode="text",
        source_path="inline://nce-emit-storyforge-build",
        source_title=display_name,
    )
    from sculpt_under_lock import resolve_sculpt_under_lock

    sculpt = (
        _default_warrior_sculpt()
        if character_id == "warrior-anthro-fox-01"
        else resolve_sculpt_under_lock(character_id)
    )
    # Prefer live mesh digests when production OBJ/FBX is present
    if sculpt.get("productionSculpt") and sculpt.get("identityLock"):
        identity_lock = {**identity_lock, **sculpt["identityLock"]}

    enriched = enrich_for_mandala(
        artifact,
        character_id=character_id,
        identity_lock=identity_lock,
        display_name=display_name,
    )
    # Prefer build_id from artifact for productionId continuity
    if artifact.build_id and not enriched.get("build_id"):
        enriched["build_id"] = artifact.build_id
    enriched.setdefault("provenance", {})
    enriched["provenance"]["sculpt"] = {
        "productionSculpt": bool(sculpt.get("productionSculpt")),
        "statusTag": sculpt.get("statusTag"),
        "meshPath": sculpt.get("meshPath"),
        "gaps": sculpt.get("gaps"),
    }

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(enriched, indent=2) + "\n", encoding="utf-8")

    mapped = map_build_to_mandala(enriched)
    gaps = [
        "identityLock_operator_supplied_not_from_story_bible",
        "audioPlan_synthesized_by_mandala_mapper",
        "visuals_still_require_sculpt_under_lock_keyframe",
    ]
    if not sculpt.get("productionSculpt"):
        gaps.append("zbrush_obj_missing_fixture_lock_digests")
    return {
        "status": "partial_with_gaps",
        "buildJson": str(out_json.resolve()),
        "buildId": enriched.get("build_id"),
        "shotListPath": getattr(artifact, "shot_list_path", None),
        "infinityRoot": str(root) if root else None,
        "productionSculpt": bool(sculpt.get("productionSculpt")),
        "sculptStatus": sculpt.get("statusTag"),
        "mandalaMap": {
            "productionId": mapped["productionId"],
            "characterId": mapped["characterId"],
            "shotCount": mapped["shotCount"],
            "identityEqual": mapped["identityEqual"],
            "scoreIdentityEqual": mapped["scoreIdentityEqual"],
        },
        "gaps": gaps,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Emit live Story Forge --build-json for Mandala")
    p.add_argument("--out", default=str(ROOT / "outputs" / "live-build.json"))
    p.add_argument("--session-id", default="nce-live-sf")
    p.add_argument("--prompt", default="Anthro fox warrior enters the fortress courtyard and looks at the gate.")
    p.add_argument("--setting", default="fortress courtyard at late-day haze")
    p.add_argument("--tone", default="cinematic")
    p.add_argument(
        "--moments",
        default="Enter courtyard,Walk to camera,Stop,Look at gate",
        help="Comma-separated key moments → SF shots",
    )
    p.add_argument("--character-id", default="warrior-anthro-fox-01")
    p.add_argument("--display-name", default="Courtyard Warrior")
    p.add_argument(
        "--identity-lock-json",
        default="",
        help="Optional path to identityLock JSON; default = sculpt_under_lock for character-id",
    )
    p.add_argument("--chapter", default="", help="Optional markdown path; uses headings as key moments")
    args = p.parse_args(argv)

    moments = [m.strip() for m in args.moments.split(",") if m.strip()]
    prompt = args.prompt
    if args.chapter:
        text = Path(args.chapter).read_text(encoding="utf-8")
        prompt = text[:2000]
        # Use ## headings as moments when present
        import re

        heads = re.findall(r"^##\s+(.+)$", text, flags=re.M)
        if heads:
            moments = [h.strip() for h in heads]

    if args.identity_lock_json:
        lock = json.loads(Path(args.identity_lock_json).read_text(encoding="utf-8"))
    elif args.character_id == "warrior-anthro-fox-01":
        lock = _default_warrior_lock()
    else:
        raise SystemExit("--identity-lock-json required for non-warrior character ids")

    result = emit_live_build(
        prompt=prompt,
        setting=args.setting,
        tone=args.tone,
        key_moments=moments,
        character_id=args.character_id,
        identity_lock=lock,
        display_name=args.display_name,
        session_id=args.session_id,
        out_json=Path(args.out),
    )
    print(json.dumps(result, indent=2))
    print("\nUse with book drop / warrior short:")
    print(f"  python3 book_drop.py --build-json {result['buildJson']} ...")
    print(f"  python3 demo_from_build.py --build-json {result['buildJson']}")
    return 0 if result["mandalaMap"]["identityEqual"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
