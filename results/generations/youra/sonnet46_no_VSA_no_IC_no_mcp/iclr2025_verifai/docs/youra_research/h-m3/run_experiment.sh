#!/bin/bash
set -e
LOG=/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_verifai/docs/youra_research/h-m3/results/run_stdout.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

CONDA_PATH=/home/PrayPrey/miniforge3
source $CONDA_PATH/etc/profile.d/conda.sh
cd /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_verifai
CLEAN_KEY=$(grep OPENAI_API_KEY .env | cut -d= -f2 | tr -d '\r')

conda run -n youra-h-m3 --no-capture-output \
    env OPENAI_API_KEY="$CLEAN_KEY" \
    python docs/youra_research/h-m3/code/run.py >> "$LOG" 2>&1
