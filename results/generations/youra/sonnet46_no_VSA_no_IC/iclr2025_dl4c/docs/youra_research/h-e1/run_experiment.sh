#!/bin/bash
set -euo pipefail
cd /home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_dl4c
LOG=docs/youra_research/h-e1/results/experiment.log
mkdir -p docs/youra_research/h-e1/results
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT
conda run -n youra-h-e1 python docs/youra_research/h-e1/code/profile_mbpp.py >> "$LOG" 2>&1
