#!/bin/bash
cd "$(dirname "$0")"
LOG=experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT
source /home/PrayPrey/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-m1
python train.py > "$LOG" 2>&1
