#!/usr/bin/env bash
# Live Story Forge emit → Mandala press-Play (sculpt under identityLock).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
export INFINITY_ROOT="${INFINITY_ROOT:-/media/jon/New Volume/Project Infinity}"
OUT_BUILD="${OUT_BUILD:-$ROOT/outputs/live-build.json}"
echo "1) Ensure ZBrush production intake folder (drop sculpt.obj when ready)"
python3 import_zbrush_production.py --character-id warrior-anthro-fox-01
echo "2) Live Story Forge emit → $OUT_BUILD"
python3 emit_storyforge_build.py --out "$OUT_BUILD" "$@"
echo "3) NCE from build-json (uses production preview if OBJ present, else fixture)"
python3 demo_from_build.py --build-json "$OUT_BUILD" --out-dir "$ROOT/outputs"
