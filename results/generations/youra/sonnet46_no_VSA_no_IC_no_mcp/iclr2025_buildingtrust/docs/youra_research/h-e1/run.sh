#!/bin/bash
set -e
cd /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_buildingtrust/docs/youra_research/h-e1/code
LOG=../experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT
python run_experiment.py > "$LOG" 2>&1
