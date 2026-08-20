#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
echo "Book drop — Archive Ch1 excerpt → Simulation Chamber (heuristic shots)"
echo "Pass --build-json from Infinity Movie Lane when available."
python3 book_drop.py --out-dir "$ROOT/outputs" "$@"
