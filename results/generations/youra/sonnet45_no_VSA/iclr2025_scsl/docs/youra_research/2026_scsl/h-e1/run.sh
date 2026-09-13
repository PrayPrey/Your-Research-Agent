#!/bin/bash
# Experiment launcher for h-e1
set -e

LOG="docs/youra_research/h-e1/experiment.log"
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

cd /workspace/TEST_scsl

# Run experiment
python docs/youra_research/h-e1/code/run_experiment.py > "$LOG" 2>&1
