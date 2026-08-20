#!/usr/bin/env bash
# Warrior courtyard press-Play short (NCE Simulation Chamber, no Cosmos).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
echo "NCE warrior short — identity-locked Simulation Chamber flipbook"
echo "Cosmos Transfer is NOT used."
python3 demo_short_warrior.py --out-dir "$ROOT/outputs" --frames-per-shot 4 --fps 8 "$@"
