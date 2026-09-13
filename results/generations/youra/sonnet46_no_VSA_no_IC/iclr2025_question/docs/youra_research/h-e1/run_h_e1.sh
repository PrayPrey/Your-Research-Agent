#!/bin/bash
set -euo pipefail

LOG=/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_question/docs/youra_research/h-e1/experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

CONDA_PATH=/home/PrayPrey/miniforge3
source $CONDA_PATH/etc/profile.d/conda.sh
conda activate youra-h-e1

export CUDA_VISIBLE_DEVICES=0
export HF_TOKEN="${HF_TOKEN}"
export TOKENIZERS_PARALLELISM=false

cd /home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_question/docs/youra_research/h-e1/code

python run_experiment.py >> "$LOG" 2>&1
