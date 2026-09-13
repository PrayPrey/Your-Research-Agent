#!/bin/bash
set -euo pipefail

LOG=experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

cd "$(dirname "$0")"

echo "Starting h-e1 experiment: $(date -Iseconds)" | tee -a "$LOG"
echo "========================================" | tee -a "$LOG"

python run_experiment.py 2>&1 | tee -a "$LOG"
