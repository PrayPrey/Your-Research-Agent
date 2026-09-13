#!/bin/bash
# Experiment launcher for h-m1 with completion marker

set -e

# Activate conda environment
source /home/anonymous/miniforge3/bin/activate youra-h-m1

# Change to code directory
cd /workspace/TEST_mldpr/docs/youra_research/h-m1/code

# Define log file
LOG="../experiment.log"

# MANDATORY: Install completion-marker finalizer
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

# Run experiment
echo "Starting experiment at $(date -Iseconds)" > "$LOG"
python main.py >> "$LOG" 2>&1

echo "Experiment finished successfully"
