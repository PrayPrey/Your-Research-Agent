#!/bin/bash
set -e

cd "$(dirname "$0")"

LOG=experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

echo "Starting H-M4 mock experiment at $(date)" | tee "$LOG"
python run_mock_experiment.py 2>&1 | tee -a "$LOG"
