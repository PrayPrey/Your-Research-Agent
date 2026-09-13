#!/bin/bash
set -e
cd /workspace/TEST_scsl/experiments/h-m1
LOG="experiment.log"
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT
python run_experiment.py > "$LOG" 2>&1
