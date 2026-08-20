"""Mythar + Beatbox / Speakers handoff for NCE (declared → partial probe).

Mandala does not compose scores. This module:
- records Mythar/audioPlan hooks
- probes Infinity BeatboxLane presence
- keeps click fallback labeled flipbook-not-motion

Live `BeatboxLane.score` invoke remains **declared** until Infinity deps + ScoreRequest
are operated outside Mandala.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from infinity_bridge import beatbox_lane_path, find_infinity_root  # noqa: E402
from mythar import accept_audio_plan  # noqa: E402

JARVIS_BEATBOX_STATUS = "http://127.0.0.1:8001/api/jarvis/beatbox-lane/status"


def probe_jarvis_beatbox_status(url: str = JARVIS_BEATBOX_STATUS) -> dict[str, Any]:
    try:
        with urllib.request.urlopen(url, timeout=2) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return {
                "ok": True,
                "httpStatus": getattr(resp, "status", None),
                "bodyPreview": body[:500],
                "status": "partial",
                "gaps": ["status_get_only_not_score_invoke"],
            }
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {
            "ok": False,
            "status": "declared",
            "gaps": ["jarvis_or_beatbox_status_unreachable"],
            "why": str(exc)[:200],
        }


def try_load_beatbox_lane() -> dict[str, Any]:
    path = beatbox_lane_path()
    if not path:
        return {
            "ok": False,
            "status": "declared",
            "gaps": ["beatbox_lane_py_missing"],
            "infinityRoot": str(find_infinity_root()) if find_infinity_root() else None,
        }
    # Do not import BeatboxLane.score here — that is Infinity's job with its env.
    return {
        "ok": True,
        "status": "partial",
        "path": str(path),
        "gaps": [
            "score_invoke_not_run_from_mandala",
            "speakers_mix_declared_until_video_path",
        ],
        "note": "File present. Call BeatboxLane.score inside Infinity, not Mandala.",
    }


def audio_handoff(audio_plan: dict[str, Any] | None) -> dict[str, Any]:
    mythar_ref = accept_audio_plan(audio_plan)
    return {
        "status": "partial_with_gaps",
        "mythar": mythar_ref,
        "jarvisBeatboxStatus": probe_jarvis_beatbox_status(),
        "beatboxLane": try_load_beatbox_lane(),
        "speakersMix": {
            "status": "declared",
            "gaps": ["requires_real_video_path_and_infinity_speakers"],
        },
        "fallback": {
            "tag": "flipbook-not-motion",
            "claim": "click bed only — not original score",
        },
        "gaps": [
            "live_beatbox_score_not_invoked_from_nce",
            "mythar_compiler_external",
            "click_fallback_until_stems",
        ],
    }


if __name__ == "__main__":
    plan = {
        "scoreIdentity": "courtyard-warrior-theme-v1",
        "statusTag": "declared",
        "cues": [],
    }
    print(json.dumps(audio_handoff(plan), indent=2))
