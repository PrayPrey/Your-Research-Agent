#!/bin/bash
cd /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/opus45/TEST_dl4c/docs/youra_research/h-m2/code
source /home/PrayPrey/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-m2

LOG=experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

echo "Starting H-M2 experiment at $(date)" > "$LOG"
python train.py >> "$LOG" 2>&1
echo "Training complete, running evaluation..." >> "$LOG"
python evaluate.py >> "$LOG" 2>&1
