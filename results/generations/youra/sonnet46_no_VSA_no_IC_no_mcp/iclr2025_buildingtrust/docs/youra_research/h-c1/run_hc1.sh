#!/bin/bash
cd /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_buildingtrust
LOG="docs/youra_research/h-c1/experiment3.log"
source /home/PrayPrey/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-c1
echo "STARTING $(date -Iseconds)" > "$LOG"
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT
PYTHONUNBUFFERED=1 python -u docs/youra_research/h-c1/code/run_experiment.py >> "$LOG" 2>&1
