#!/bin/bash
LOG=/home/PrayPrey/YouRA_no_IC_opus45/TEST_wsl/docs/youra_research/h-m4/code/experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

source ~/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-m4
export LD_LIBRARY_PATH=/home/PrayPrey/miniforge3/envs/youra-h-m4/lib:$LD_LIBRARY_PATH

timeout 3600 python run_experiment.py \
    --n-models 1200 \
    --n-train 1000 \
    --n-test 200 \
    --n-seeds 10 \
    --epochs 50 \
    --device cpu >> "$LOG" 2>&1
