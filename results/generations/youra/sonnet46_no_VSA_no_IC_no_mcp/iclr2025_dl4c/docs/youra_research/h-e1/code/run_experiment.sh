#!/bin/bash
# Full experiment runner for H-E1
# Mandatory: trap EXIT with EXPERIMENT COMPLETE marker

LOG="experiment.log"
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

CONDA_PATH="/home/PrayPrey/miniforge3"
ENV_NAME="youra-h-e1"
source "$CONDA_PATH/etc/profile.d/conda.sh"
conda activate "$ENV_NAME"

echo "=== H-E1 Experiment Start $(date -Iseconds) ===" >> "$LOG"
echo "GPU info:" >> "$LOG"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader >> "$LOG" 2>&1

python run_experiment.py config.yaml >> "$LOG" 2>&1
