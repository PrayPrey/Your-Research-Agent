#!/bin/bash
set -e

LOG=logs/experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

echo "Installing dependencies..."
pip install -q -r requirements.txt

echo "Running H-E1 experiment..."
python main.py 2>&1 | tee "$LOG"

echo "Experiment finished successfully"
