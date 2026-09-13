#!/bin/bash
set -e

cd "$(dirname "$0")/.."

LOG=logs/experiment.log
mkdir -p logs

# Completion marker finalizer
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

export CUDA_VISIBLE_DEVICES=0

echo "Starting training..." | tee -a "$LOG"
python3 scripts/train.py 2>&1 | tee -a "$LOG"

echo "Starting evaluation..." | tee -a "$LOG"
python3 scripts/evaluate.py 2>&1 | tee -a "$LOG"

echo "Experiment complete." | tee -a "$LOG"
