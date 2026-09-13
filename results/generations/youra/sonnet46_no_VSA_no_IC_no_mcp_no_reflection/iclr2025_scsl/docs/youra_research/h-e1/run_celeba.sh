#!/bin/bash
LOG=/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet46/TEST_scsl/docs/youra_research/h-e1/experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

source /home/PrayPrey/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-e1-scsl

cd /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet46/TEST_scsl/docs/youra_research/h-e1/code

PYTHONUNBUFFERED=1 python experiment.py \
    --wilds-root /home/PrayPrey/.wilds_cache \
    --wilds-root-celeba /home/PrayPrey/.wilds \
    --output-dir ./outputs \
    --figures-dir ../figures \
    --results-file ./outputs/results.csv \
    --experiment-json ../experiment_results.json \
    --dataset both \
    --device cuda:2 \
    2>&1 | tee -a "$LOG"
