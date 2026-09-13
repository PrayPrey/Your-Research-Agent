#!/bin/bash
set -e

LOG=/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_dl4c/docs/youra_research/h-m2/experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

CONDA_PATH="/home/PrayPrey/miniforge3"
source $CONDA_PATH/etc/profile.d/conda.sh
conda activate youra-h-m2

cd /home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_dl4c

CUDA_VISIBLE_DEVICES=0 conda run -n youra-h-m2 \
    python docs/youra_research/h-m2/code/run_experiment.py \
    >> "$LOG" 2>&1
