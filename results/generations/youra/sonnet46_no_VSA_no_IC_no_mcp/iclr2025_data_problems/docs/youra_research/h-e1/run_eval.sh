#!/usr/bin/env bash
set -euo pipefail

LOG=/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_data_problems/docs/youra_research/h-e1/eval.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

source /home/PrayPrey/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-e1

cd /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_data_problems/docs/youra_research/h-e1/code

python run_evaluation.py >> "$LOG" 2>&1
