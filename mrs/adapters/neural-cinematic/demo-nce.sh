#!/usr/bin/env bash
# NCE local demo — Simulation Chamber flipbook (+ optional SD-Turbo AI Painter).
# Cosmos Transfer is NOT invoked.
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd -- "${ROOT}/../../../.." && pwd)"

echo "============================================================"
echo " Mandala NCE — Simulation Chamber (Cosmos NOT required)"
echo "============================================================"
echo "Package: ${ROOT}"
echo "Repo:    ${REPO}"
echo
echo "Organs:"
echo "  Story Forge     = narrative law (boundary only)"
echo "  Mandala         = visual body (this package)"
echo "  Mythar          = sonic breath (declared hooks)"
echo "  AAIS            = factory worker stubs (declared)"
echo "  Sim Chamber     = motion organ (partial flipbook)"
echo "  AI Painter      = SD-Turbo :13305 (partial_with_gaps)"
echo "  Cosmos          = optional / SKIPPED"
echo "============================================================"

port_in_use() {
  ss -ltn 2>/dev/null | awk '{print $4}' | grep -qE "[:.]${1}$"
}

probe() {
  local port="$1"
  if port_in_use "${port}"; then
    echo "  :${port}  UP"
  else
    echo "  :${port}  down"
  fi
}

echo
echo "Listening:"
probe 13305
probe 13306

START_ALL="${REPO}/tools/sd-bridge/start_all.sh"
DRY=0
for arg in "$@"; do
  if [[ "${arg}" == "--dry-run" ]]; then DRY=1; fi
done

if [[ "${DRY}" -eq 0 ]] && ! port_in_use 13305; then
  if [[ -f "${START_ALL}" ]]; then
    echo
    echo "Bridge :13305 down — attempting tools/sd-bridge/start_all.sh ..."
    mkdir -p "${REPO}/runtime/logs"
    nohup bash "${START_ALL}" >"${REPO}/runtime/logs/nce-start-all.log" 2>&1 &
    echo $! >"${REPO}/runtime/logs/nce-start-all.pid"
    for _ in $(seq 1 25); do
      if port_in_use 13305; then
        echo "Bridge up on :13305."
        break
      fi
      sleep 0.4
    done
    if ! port_in_use 13305; then
      echo "Bridge still down — painter will tag beauty_skipped_bridge_down."
    fi
  fi
fi

export LEMONADE_API_BASE="${LEMONADE_API_BASE:-http://127.0.0.1:13305/api/v1}"
unset LEMONADE_PORT LEMONADE_HOST || true

cd "${ROOT}"
python3 demo_pipeline.py "$@"
