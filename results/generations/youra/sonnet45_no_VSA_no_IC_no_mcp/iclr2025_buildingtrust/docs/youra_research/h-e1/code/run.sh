#!/bin/bash
set -euo pipefail

LOG="experiment.log"
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

cd "$(dirname "$0")"

echo "Starting h-e1 experiment at $(date)" | tee "$LOG"
python -u src/run_experiment.py 2>&1 | tee -a "$LOG"
