#!/bin/bash
# H-E1 experiment launcher
LOG=docs/youra_research/h-e1/code/experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

source /home/PrayPrey/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-e1
python docs/youra_research/h-e1/code/run.py >> "$LOG" 2>&1
