"""Mythar — Sonic Breath Organ (adapter boundary).

Mythar exists in-repo as encoder / narrative adapters
(`mrs/packages/mythar-encoder`, `mrs/narrative/mythar-*.js`) and SRE sketch.
This stub does **not** invent a full audio engine. It accepts storyforge-boundary
1.1-shaped `audioPlan` / `scoreIdentity` hooks for handoff evidence only.

Status: **declared** (boundary + validation of refs) with explicit `gaps: []`.
Live TTS/Beatbox = external.
"""

from __future__ import annotations

from typing import Any

STATUS = "declared"

GAPS = [
    "no_tts_or_beatbox_synthesis_in_nce",
    "audio_plan_hooks_only_not_rendered_stems",
    "phonosemantic_cadence_not_executed_here",
]

LIMITATION = (
    "Mythar owns breath-state, phonosemantic cadence, and soundscapes. "
    "NCE records audioPlan/scoreIdentity for alignment; it does not synthesize "
    "ritual audio or replace Beatbox / Mythar TTS."
)

IN_REPO_SURFACES = (
    "mrs/packages/mythar-encoder",
    "mrs/narrative/mythar-adapters.js",
    "mrs/narrative/mythar-integration.js",
    "mrs/adapters/storyforge-boundary contract audioPlan (1.1)",
)


class MytharBoundaryError(ValueError):
    pass


def accept_audio_plan(audio_plan: dict[str, Any] | None) -> dict[str, Any] | None:
    """Validate optional audioPlan hooks; return normalized mytharAudioRef or None."""
    if audio_plan is None:
        return None
    if not isinstance(audio_plan, dict):
        raise MytharBoundaryError("audioPlan must be an object or null")
    score = audio_plan.get("scoreIdentity")
    if score is not None and (not isinstance(score, str) or not score.strip()):
        raise MytharBoundaryError("audioPlan.scoreIdentity must be a non-empty string when set")
    return {
        "organ": "Mythar",
        "role": "Sonic Breath",
        "status": STATUS,
        "scoreIdentity": score,
        "cueCount": len(audio_plan.get("cues") or []) if isinstance(audio_plan.get("cues"), list) else 0,
        "mappingStatusTag": audio_plan.get("mappingStatusTag") or audio_plan.get("statusTag"),
        "limitation": LIMITATION,
        "inRepoSurfaces": list(IN_REPO_SURFACES),
        "gaps": list(GAPS),
    }
