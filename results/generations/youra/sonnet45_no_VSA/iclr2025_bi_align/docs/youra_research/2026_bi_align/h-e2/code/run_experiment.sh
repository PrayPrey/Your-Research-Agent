#!/bin/bash

# H-E2 SAT Profiling Experiment Runner
# Implements experiment launcher rules with completion marker

set -e

cd "$(dirname "$0")"

# Setup paths
EXPERIMENT_DIR="$(pwd)"
LOG="$EXPERIMENT_DIR/experiment.log"

# Install completion marker finalizer (MANDATORY)
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

# Log start
echo "================================================================================" | tee -a "$LOG"
echo "H-E2 SAT Profiling Experiment - Started at $(date)" | tee -a "$LOG"
echo "================================================================================" | tee -a "$LOG"

# Check for CUDA
if ! command -v nvidia-smi &> /dev/null; then
    echo "WARNING: nvidia-smi not found. Running on CPU (profiling will be limited)" | tee -a "$LOG"
fi

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..." | tee -a "$LOG"
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip >> "$LOG" 2>&1
    pip install -r requirements.txt >> "$LOG" 2>&1
else
    source venv/bin/activate
fi

# Run experiment
echo "Starting experiment..." | tee -a "$LOG"
cd src
python main.py 2>&1 | tee -a "$LOG"

EXIT_CODE=${PIPESTATUS[0]}

echo "================================================================================" | tee -a "$LOG"
echo "Experiment finished with exit code: $EXIT_CODE" | tee -a "$LOG"
echo "================================================================================" | tee -a "$LOG"

exit $EXIT_CODE
