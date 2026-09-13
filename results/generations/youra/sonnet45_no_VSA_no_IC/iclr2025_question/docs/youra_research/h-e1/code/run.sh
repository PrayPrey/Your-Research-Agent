#!/bin/bash
# Experiment launcher with completion marker (MANDATORY for unattended mode)

LOG=experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

source /home/PrayPrey/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-e1

python run_experiment.py > "$LOG" 2>&1
