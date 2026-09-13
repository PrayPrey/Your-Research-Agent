#!/bin/bash
set -euo pipefail
cd /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_question
LOG=docs/youra_research/h-m1/results/experiment.log
mkdir -p docs/youra_research/h-m1/results
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT
python docs/youra_research/h-m1/code/run.py "$@" 2>&1 | tee -a "$LOG"
