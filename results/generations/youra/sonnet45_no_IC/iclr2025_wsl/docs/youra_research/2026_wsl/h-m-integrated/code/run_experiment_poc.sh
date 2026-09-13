#!/bin/bash
# PoC-scale experiment for H-M-Integrated CAPE validation
# Reduced scale for faster execution while proving mechanism works

set -euo pipefail

# Conda setup
CONDA_PATH="/home/anonymous/miniforge3"
source "$CONDA_PATH/etc/profile.d/conda.sh"
conda activate youra-h-m-integrated

# Navigate to code folder
cd /workspace/TEST_wsl/docs/youra_research/h-m-integrated/code

# Install completion-marker trap (MANDATORY per workflow rules)
LOG="experiment_results.log"
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

echo "Starting PoC-scale CAPE experiment..." | tee -a "$LOG"
echo "Using existing data (inherited from h-e1)" | tee -a "$LOG"

# Execute main experiment script with PoC-scale settings
# --epochs reduced to 10 (from 100) for PoC
# Using existing 100-model dataset (not full 400)
python run_experiment.py \
    --epochs 10 \
    --batch-size 16 \
    --lr 1e-4 \
    --models-per-arch 25 \
    --output-dir results_poc \
    --seed 42 \
    2>&1 | tee -a "$LOG"

echo "Experiment completed" | tee -a "$LOG"
