#!/bin/bash
set -e

export CUDA_VISIBLE_DEVICES=""  # Force CPU

cd "$(dirname "$0")"
LOG=poc_experiment.log

trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

python main.py --poc > "$LOG" 2>&1
