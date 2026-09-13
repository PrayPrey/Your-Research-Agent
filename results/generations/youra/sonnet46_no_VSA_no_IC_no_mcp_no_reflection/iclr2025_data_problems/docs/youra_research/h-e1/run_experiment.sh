#!/bin/bash
# H-E1 experiment launcher using youra-h-e1-v2 env
set -e

PYTHON=/home/PrayPrey/miniforge3/envs/youra-h-e1-v2/bin/python
CODE=/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet46/TEST_data_problems/docs/youra_research/h-e1/code
LOG=/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet46/TEST_data_problems/docs/youra_research/h-e1/experiment.log

trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

cd "$CODE"
export PYTHONPATH="$CODE:$PYTHONPATH"

echo "Starting H-E1 experiment at $(date -Iseconds)" | tee -a "$LOG"
"$PYTHON" run.py 2>&1 | tee -a "$LOG"
