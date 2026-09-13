#!/bin/bash
# H-E1 Experiment Launcher — MANDATORY COMPLETION MARKER PATTERN
set -e

LOG=/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_scope/docs/youra_research/h-e1/code/experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

cd /home/PrayPrey/YouRA_no_IC_sonnet46/TEST_scope/docs/youra_research/h-e1/code

source /home/PrayPrey/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-e1-v2

python run_experiment.py \
    --models bert-base-uncased microsoft/deberta-v3-base google/vit-base-patch16-224 \
    --max-workers 1 \
    --output-dir /home/PrayPrey/YouRA_no_IC_sonnet46/TEST_scope/docs/youra_research/h-e1 \
    --resume \
    >> "$LOG" 2>&1
