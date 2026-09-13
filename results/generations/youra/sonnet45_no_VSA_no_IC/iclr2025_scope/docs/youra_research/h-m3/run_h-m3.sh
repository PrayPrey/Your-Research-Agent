#!/bin/bash
set -e

# Conda activation
source /home/PrayPrey/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-m3

# Change to code directory
cd code

# Run experiment
LOG=../experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

echo "Starting H-M3 experiment at $(date)" > "$LOG"
python run_experiment.py 2>&1 | tee -a "$LOG"

