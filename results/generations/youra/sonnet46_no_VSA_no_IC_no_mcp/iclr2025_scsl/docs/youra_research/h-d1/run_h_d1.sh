#!/bin/bash
set -e
LOG=/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_scsl/docs/youra_research/h-d1/experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

cd /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_scsl/docs/youra_research/h-d1/code
/home/PrayPrey/miniforge3/envs/youra-h-e1/bin/python3 run_experiment.py > "$LOG" 2>&1
