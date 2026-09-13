#!/bin/bash
set -e
cd /home/PrayPrey/YouRA_no_IC_opus45/TEST_scope/docs/youra_research/h-e1/code
source /home/PrayPrey/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-e1

LOG=/home/PrayPrey/YouRA_no_IC_opus45/TEST_scope/docs/youra_research/h-e1/experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

echo "Starting H-E1 experiment at $(date)" >> "$LOG"
python run_experiment.py >> "$LOG" 2>&1

echo "Running clustering..." >> "$LOG"
python cluster.py >> "$LOG" 2>&1

echo "Generating visualizations..." >> "$LOG"
python visualize.py >> "$LOG" 2>&1
