#!/bin/bash
# H-M1 experiment launcher (mandatory trap pattern)
set -e

cd /home/PrayPrey/YouRA_no_IC_sonnet46/TEST_verifai

LOG=/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_verifai/docs/youra_research/h-m1/experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

source /home/PrayPrey/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-m1

PYTHONPATH=experiments/h-m1 python experiments/h-m1/run_vllm.py > "$LOG" 2>&1
