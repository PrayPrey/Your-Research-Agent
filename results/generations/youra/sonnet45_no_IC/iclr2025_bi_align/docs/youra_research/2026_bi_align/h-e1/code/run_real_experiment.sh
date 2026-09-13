#!/bin/bash
set -e

# Activate conda environment
source /home/anonymous/miniforge3/bin/activate youra-h-e1

# Set experiment directory
cd /workspace/TEST_bi_align/docs/youra_research/h-e1/code

# Set log file
LOG="experiment.log"

# Install completion marker on exit
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

# Run experiment
echo "Starting experiment at $(date -Iseconds)" > "$LOG"
echo "Using GPU: $CUDA_VISIBLE_DEVICES" >> "$LOG"

python run_poc_experiment.py >> "$LOG" 2>&1

echo "Experiment completed at $(date -Iseconds)" >> "$LOG"
