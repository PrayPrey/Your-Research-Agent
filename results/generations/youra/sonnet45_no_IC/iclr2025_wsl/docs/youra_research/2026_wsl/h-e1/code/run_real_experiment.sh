#!/bin/bash
# Run experiment with real HuggingFace models

cd /workspace/TEST_wsl/docs/youra_research/h-e1/code

# Setup conda
source /home/anonymous/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-e1

# Set log file
LOG="experiment.log"

# Install completion marker finalizer (MANDATORY)
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

# Run experiment
echo "Starting experiment with REAL HuggingFace models..." > "$LOG"
echo "Timestamp: $(date -Iseconds)" >> "$LOG"
echo "" >> "$LOG"

python run_experiment.py >> "$LOG" 2>&1

EXIT_CODE=$?
echo "" >> "$LOG"
echo "Python exit code: $EXIT_CODE" >> "$LOG"

exit $EXIT_CODE
