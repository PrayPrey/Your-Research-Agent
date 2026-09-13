#!/bin/bash
set -e

# Experiment launcher for h-m1
# Ensures proper Python path and conda environment

cd "$(dirname "$0")"

# Activate conda environment
source /home/anonymous/miniforge3/bin/activate youra-h-m1

# Set PYTHONPATH to include both h-m1 and h-e1 (h-m1 first)
export PYTHONPATH="$(pwd):$(pwd)/../../h-e1/code"

# Run experiment with proper logging
LOG=experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

echo "Starting h-m1 experiment..."
echo "Working directory: $(pwd)"
echo "Python: $(which python)"
echo "PYTHONPATH: $PYTHONPATH"
echo "Log file: $LOG"
echo ""

# Run with timeout (1 hour max)
timeout 3600 python run_h_m1_experiment_simple.py 2>&1 | tee "$LOG"
EXIT_CODE=${PIPESTATUS[0]}

echo ""
echo "Experiment completed with exit code: $EXIT_CODE"
exit $EXIT_CODE
