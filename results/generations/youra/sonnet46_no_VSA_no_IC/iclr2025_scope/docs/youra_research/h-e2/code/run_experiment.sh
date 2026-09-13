#!/bin/bash
# h-e2 experiment launcher
set -e
cd "$(dirname "$0")"

LOG=experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

source /home/PrayPrey/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-e2

python run_experiment.py \
    --model-name meta-llama/Llama-2-7b-hf \
    --swa-k 4 \
    --swa-window-size 512 \
    --calib-n-sequences 100 \
    --eval-max-length 4096 \
    --eval-stride 512 \
    --verify-seq-len 600 \
    --results-dir results \
    --figures-dir ../figures \
    --seed 1 \
    2>&1 | tee "$LOG"
