#!/bin/bash
# Full experiment launcher for H-M2
cd /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_data_problems
LOG=docs/youra_research/h-m2/experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

export CUDA_VISIBLE_DEVICES=1
export HF_DATASETS_OFFLINE=0
export TOKENIZERS_PARALLELISM=false

CONDA_PATH=/home/PrayPrey/miniforge3
source $CONDA_PATH/etc/profile.d/conda.sh

conda run -n youra-h-m2 python docs/youra_research/h-m2/code/run_experiment.py \
    --device cuda \
    --results-path docs/youra_research/h-m2/experiment_results.json \
    --log-level INFO \
    >> "$LOG" 2>&1
