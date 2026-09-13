#!/bin/bash
# Run from h-e1/code directory so imports work
H_E1_CODE="/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_dl4c/docs/youra_research/h-e1/code"
HM2_CODE="/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_dl4c/docs/youra_research/h-m2/code"
LOG="$HM2_CODE/experiment.log"

trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

source /home/PrayPrey/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-e1

cd "$H_E1_CODE"
PYTHONPATH="$H_E1_CODE:$PYTHONPATH" python "$HM2_CODE/generate_reward_log.py" >> "$LOG" 2>&1
