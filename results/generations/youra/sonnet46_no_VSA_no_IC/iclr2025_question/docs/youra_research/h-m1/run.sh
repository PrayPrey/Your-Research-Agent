#!/bin/bash
set -euo pipefail
LOG="$(dirname "$(realpath "$0")")/experiment.log"
PY="/home/PrayPrey/miniforge3/envs/youra-h-e1-final/bin/python3"
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT
cd "$(dirname "$(realpath "$0")")/code"
"$PY" run_experiment.py > "$LOG" 2>&1
