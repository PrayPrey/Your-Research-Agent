#!/bin/bash
set -euo pipefail

LOG=docs/youra_research/h-m3/experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

cd /home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_dl4c
python docs/youra_research/h-m3/code/run_experiment.py > "$LOG" 2>&1
