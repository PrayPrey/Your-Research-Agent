#!/bin/bash
# Experiment launcher with real dataset
# Includes mandatory completion marker and timeout protection

set -euo pipefail

CODE_DIR="/workspace/TEST_buildingtrust/docs/youra_research/h-e1/code"
LOG="${CODE_DIR}/experiment.log"

# MANDATORY: Install completion-marker finalizer FIRST
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

# Load environment variables (API keys)
if [ -f "/workspace/TEST_buildingtrust/.env" ]; then
    export $(grep -v '^#' /workspace/TEST_buildingtrust/.env | xargs)
fi

# Activate conda environment
source /home/anonymous/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-e1

# Change to code directory
cd "$CODE_DIR"

# Run experiment with timeout (4 hours = 14400 seconds)
echo "Starting experiment at $(date -Iseconds)" > "$LOG"
echo "Using REAL TruthfulQA dataset" >> "$LOG"
echo "================================================" >> "$LOG"

timeout 14400 python run_experiment.py >> "$LOG" 2>&1 || {
    exit_code=$?
    if [ $exit_code -eq 124 ]; then
        echo "ERROR: Experiment timed out after 4 hours" >> "$LOG"
    fi
    exit $exit_code
}
