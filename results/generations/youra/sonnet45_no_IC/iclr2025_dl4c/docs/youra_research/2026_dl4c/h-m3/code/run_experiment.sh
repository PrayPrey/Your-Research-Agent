#!/bin/bash
set -e

# Experiment launcher with proper completion tracking
LOG=experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate conda environment
source /home/anonymous/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-m3

# Run experiment (CPU mode since GPU unavailable)
echo "Starting Phase 3 experiment with real dataset..." | tee -a "$LOG"
echo "Using CPU mode (GPU driver incompatible)" | tee -a "$LOG"
echo "" | tee -a "$LOG"

python run_phase3_experiment.py 2>&1 | tee -a "$LOG"

echo "" | tee -a "$LOG"
echo "Experiment execution finished" | tee -a "$LOG"
