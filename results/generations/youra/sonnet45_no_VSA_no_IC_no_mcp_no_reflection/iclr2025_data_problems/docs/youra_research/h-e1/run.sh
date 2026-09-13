#!/bin/bash
# H-E1 Experiment Launcher

set -e

LOG="experiment.log"
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

cd "$(dirname "$0")/code"

echo "[$(date -Iseconds)] Starting H-E1 experiment..." | tee -a "$LOG"

# Install dependencies
pip install -r requirements.txt >> "$LOG" 2>&1

# Run experiment
python run_experiment.py 2>&1 | tee -a "$LOG"

echo "[$(date -Iseconds)] Experiment finished" | tee -a "$LOG"
