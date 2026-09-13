#!/bin/bash
set -e
cd "$(dirname "$0")"

LOG=experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

# Clear old results
rm -f results/samples.json results/results.json

# Run with timeout (30 min max)
timeout 1800 python -u run_analysis.py > "$LOG" 2>&1
