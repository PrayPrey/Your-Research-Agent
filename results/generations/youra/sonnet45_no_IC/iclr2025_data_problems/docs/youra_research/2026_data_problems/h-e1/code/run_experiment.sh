#!/bin/bash

# Experiment launcher for h-e1
# MANDATORY: Install completion marker finalizer

set -e

cd "$(dirname "$0")"

LOG="experiment.log"

# MANDATORY: Completion marker trap (fires on any exit)
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

echo "Starting experiment at $(date -Iseconds)" | tee "$LOG"
echo "Using conda environment: youra-h-e1" | tee -a "$LOG"

# Activate conda environment
source /home/anonymous/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-e1

# Run experiment with timeout (4 hours max)
timeout 14400 python run_experiment.py 2>&1 | tee -a "$LOG"

echo "Experiment finished at $(date -Iseconds)" | tee -a "$LOG"
