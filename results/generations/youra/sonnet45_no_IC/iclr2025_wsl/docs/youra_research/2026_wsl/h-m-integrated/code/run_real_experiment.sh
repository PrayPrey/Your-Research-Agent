#!/bin/bash
# Run CAPE training experiment with real HuggingFace models

cd /workspace/TEST_wsl/docs/youra_research/h-m-integrated/code

# Setup conda
source /home/anonymous/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-m-integrated

# Set log file
LOG="experiment.log"

# Install completion marker finalizer (MANDATORY)
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

# Run CAPE training with real models
echo "Starting CAPE training with REAL HuggingFace models..." > "$LOG"
echo "Timestamp: $(date -Iseconds)" >> "$LOG"
echo "" >> "$LOG"

python train_cape.py >> "$LOG" 2>&1

EXIT_CODE=$?
echo "" >> "$LOG"
echo "Python exit code: $EXIT_CODE" >> "$LOG"

exit $EXIT_CODE
