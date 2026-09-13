#!/bin/bash
set -e
cd "$(dirname "$0")"

LOG=experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

source /home/PrayPrey/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-m2

echo "Starting H-M2 experiment at $(date)" | tee "$LOG"
python train.py 2>&1 | tee -a "$LOG"
