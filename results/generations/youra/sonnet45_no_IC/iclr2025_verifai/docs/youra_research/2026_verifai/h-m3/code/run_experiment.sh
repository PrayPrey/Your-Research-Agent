#!/bin/bash
# H-M3 Experiment Runner
# CRITICAL: Includes completion marker finalizer (prevents unrecoverable hangs)

LOG="experiment.log"

# Install completion marker finalizer FIRST (MANDATORY!)
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

# Activate conda environment
source /home/anonymous/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-m3

# Run experiment
cd "$(dirname "$0")"
python src/main.py 2>&1 | tee "$LOG"
