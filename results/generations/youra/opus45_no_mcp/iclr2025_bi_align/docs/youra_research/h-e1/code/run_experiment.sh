#!/bin/bash
# Experiment runner for H-E1 with completion marker
cd /home/PrayPrey/YouRA_results_new_4_opus45_no_mcp/TEST_bi_align/docs/youra_research/h-e1/code

LOG=experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

source /home/PrayPrey/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-e1

python run_experiment.py > "$LOG" 2>&1
