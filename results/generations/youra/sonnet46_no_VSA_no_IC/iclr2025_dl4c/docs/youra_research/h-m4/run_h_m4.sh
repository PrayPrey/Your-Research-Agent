#!/bin/bash
set -e
cd /home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_dl4c

LOG=docs/youra_research/h-m4/experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

source /home/PrayPrey/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-m4

python docs/youra_research/h-m4/code/run_experiment.py > "$LOG" 2>&1
