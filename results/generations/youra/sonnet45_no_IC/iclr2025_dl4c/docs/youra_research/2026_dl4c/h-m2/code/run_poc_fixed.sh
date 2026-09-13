#!/bin/bash
# PoC Experiment Launcher with REAL dataset evaluation
# Fixed version - no mock data

set -e

# Setup
export PYTHONPATH="${PWD}:${PYTHONPATH}"
LOG="${PWD}/experiment.log"

# Install completion marker finalizer (MANDATORY)
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

# Activate conda environment
source /home/anonymous/miniforge3/bin/activate youra-h-e1

# Run experiment with real data
echo "Starting PoC experiment with REAL dataset (HumanEval + MBPP)..." | tee -a "$LOG"
echo "Timestamp: $(date -Iseconds)" | tee -a "$LOG"
echo "" | tee -a "$LOG"

python run_poc_experiment.py 2>&1 | tee -a "$LOG"

echo "" | tee -a "$LOG"
echo "PoC experiment finished at $(date -Iseconds)" | tee -a "$LOG"
