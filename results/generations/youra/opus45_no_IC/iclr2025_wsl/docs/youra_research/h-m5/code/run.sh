#!/bin/bash
# H-M5 Experiment Runner

CONDA_PATH=/home/PrayPrey/miniforge3
source "$CONDA_PATH/etc/profile.d/conda.sh"
conda activate youra-h-m5
export LD_LIBRARY_PATH=$CONDA_PATH/envs/youra-h-m5/lib:$LD_LIBRARY_PATH

cd "$(dirname "$0")"

LOG=experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

timeout 7200 python run_experiment.py \
    --n-seeds 10 \
    --epochs 50 \
    --batch-size 64 \
    --device cuda \
    --output-dir "$(dirname "$PWD")" \
    > "$LOG" 2>&1
