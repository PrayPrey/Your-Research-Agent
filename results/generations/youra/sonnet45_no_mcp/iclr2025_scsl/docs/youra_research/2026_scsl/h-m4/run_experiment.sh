#!/bin/bash
# H-M4 Geometry-Phenotype Coupling Experiment Runner
# Phase 4 Implementation

set -e  # Exit on error

# Experiment log
LOG="experiment.log"
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

# Set GPU
export CUDA_VISIBLE_DEVICES=0

# Navigate to code directory
cd "$(dirname "$0")/code"

echo "Starting H-M4 Experiment at $(date)" | tee -a "$LOG"
echo "Working directory: $(pwd)" | tee -a "$LOG"
echo "GPU: $CUDA_VISIBLE_DEVICES" | tee -a "$LOG"

# Run experiment with timeout (4 hours max)
timeout 14400 python3 run_experiment.py 2>&1 | tee -a "$LOG"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "Experiment completed successfully" | tee -a "$LOG"
elif [ $EXIT_CODE -eq 124 ]; then
    echo "Experiment timed out after 4 hours" | tee -a "$LOG"
    exit 1
else
    echo "Experiment failed with exit code $EXIT_CODE" | tee -a "$LOG"
    exit $EXIT_CODE
fi
