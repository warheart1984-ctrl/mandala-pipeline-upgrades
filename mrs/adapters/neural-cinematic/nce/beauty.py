"""Deprecated alias — use ai_painter.paint_keyframe (organ: AI Painter)."""

from ai_painter import paint_keyframe, probe_bridge, lemonade_base_url

# Back-compat name used in early scaffold drafts
polish_keyframe = paint_keyframe

__all__ = ["paint_keyframe", "polish_keyframe", "probe_bridge", "lemonade_base_url"]
