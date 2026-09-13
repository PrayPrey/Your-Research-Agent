#!/bin/bash
set -e

LOG=/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet46/TEST_scsl/docs/youra_research/h-e1/experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

CONDA_PATH=/home/PrayPrey/miniforge3
source $CONDA_PATH/etc/profile.d/conda.sh

CODE_DIR=/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet46/TEST_scsl/docs/youra_research/h-e1/code

cd $CODE_DIR

conda run -n youra-h-e1-scsl python experiment.py \
    --wilds-root /home/PrayPrey/.wilds_cache \
    --wilds-root-celeba /home/PrayPrey/.wilds \
    --output-dir ./outputs \
    --figures-dir ../figures \
    --results-file ./outputs/results.csv \
    --experiment-json ../experiment_results.json \
    --dataset both \
    --device cuda:1 \
    2>&1 | tee -a "$LOG"
