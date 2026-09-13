#!/bin/bash
LOG=docs/youra_research/h-m2/dry_run.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT
CONDA_PATH=/home/PrayPrey/miniforge3
source $CONDA_PATH/etc/profile.d/conda.sh
conda run -n youra-h-m2 python docs/youra_research/h-m2/code/run_experiment.py \
    --dry-run \
    --dry-run-items 60 \
    --device cuda \
    --results-path docs/youra_research/h-m2/dry_run_result.json \
    --log-level INFO \
    >> "$LOG" 2>&1
