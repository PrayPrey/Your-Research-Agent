#!/bin/bash
# Experiment launcher for h-m1 with completion marker
set -euo pipefail

cd "$(dirname "$0")"
LOG="experiment.log"

# Install completion marker (EXIT trap)
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

echo "Starting h-m1 experiment at $(date -Iseconds)" | tee -a "$LOG"

# Run experiment
python code/run_experiment.py 2>&1 | tee -a "$LOG"

echo "Experiment finished at $(date -Iseconds)" | tee -a "$LOG"
