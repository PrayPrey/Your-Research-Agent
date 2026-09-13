#!/bin/bash
# Run H-E1 Temperature Scaling Calibration Experiment

set -e  # Exit on error

# Experiment directory
EXPERIMENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$EXPERIMENT_DIR"

# Log file
LOG_FILE="logs/experiment.log"
mkdir -p logs

# Install completion marker finalizer (MANDATORY)
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG_FILE"' EXIT

# Create directories
mkdir -p figures results data/cache models/cache

# Install dependencies
echo "Installing dependencies..." | tee -a "$LOG_FILE"
pip install -r requirements.txt >> "$LOG_FILE" 2>&1

# Run experiment
echo "Starting experiment at $(date)" | tee -a "$LOG_FILE"
python main.py 2>&1 | tee -a "$LOG_FILE"

echo "Experiment finished at $(date)" | tee -a "$LOG_FILE"
