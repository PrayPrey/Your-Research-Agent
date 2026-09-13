#!/bin/bash
set -e
cd "$(dirname "$0")"
LOG=experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

python3 code/run_experiment.py \
    --checkpoint_dir h-e1/checkpoints \
    --results_dir h-e1/results \
    --figures_dir h-e1/figures \
    --seed 42 \
    --skip_finetuning \
    --n_bootstrap 200 \
    --n_permutations 1000 \
    >> "$LOG" 2>&1
