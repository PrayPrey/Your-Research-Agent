#!/bin/bash
set -e

# Change to code directory first
cd "$(dirname "$0")/code"

# Ensure results directory exists
mkdir -p results

LOG="results/experiment.log"

# Install completion marker finalizer (MANDATORY)
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

# Set library path to use system libraries
export LD_LIBRARY_PATH=/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH

# Run experiment
python3 run.py 2>&1 | tee -a "$LOG"
