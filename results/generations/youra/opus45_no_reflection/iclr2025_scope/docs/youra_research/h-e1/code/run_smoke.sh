#!/bin/bash
# H-E1 Smoke Test Runner
cd "$(dirname "$0")"
LOG=experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

# Use smoke config
cp config_smoke.py config.py

export CUDA_VISIBLE_DEVICES=0
python run_experiment.py 2>&1 | tee "$LOG"
