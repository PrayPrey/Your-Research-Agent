#!/bin/bash
# Real experiment launcher for h-m1
# Runs the main h-m1 experiment with actual model training

set -euo pipefail

# Get absolute path to h-m1 code directory
CODE_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$CODE_DIR"

LOG="experiment.log"

# MANDATORY: Install completion-marker finalizer
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

# Activate conda environment
source /home/anonymous/miniforge3/bin/activate youra-h-m1

echo "========================================" | tee -a "$LOG"
echo "H-M1 Real Experiment Launcher" | tee -a "$LOG"
echo "Using REAL HumanEval + MBPP with actual PPO training" | tee -a "$LOG"
echo "Start: $(date -Iseconds)" | tee -a "$LOG"
echo "Working directory: $CODE_DIR" | tee -a "$LOG"
echo "========================================" | tee -a "$LOG"

# Set PYTHONPATH to include h-m1 and h-e1 code directories
export PYTHONPATH="$CODE_DIR:$CODE_DIR/../../h-e1/code:${PYTHONPATH:-}"

echo "PYTHONPATH: $PYTHONPATH" | tee -a "$LOG"
echo "Python: $(which python)" | tee -a "$LOG"
echo "" | tee -a "$LOG"

# Run the main h-m1 experiment (REAL datasets + REAL model training)
# Use explicit paths to avoid import issues
cd "$CODE_DIR"
exec python "$CODE_DIR/run_h_m1_experiment.py" 2>&1 | tee -a "$LOG"
