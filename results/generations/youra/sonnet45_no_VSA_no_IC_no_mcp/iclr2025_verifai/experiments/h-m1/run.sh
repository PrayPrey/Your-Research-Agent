#!/bin/bash
set -e

LOG=experiments/h-m1/logs/experiment.log
mkdir -p experiments/h-m1/logs

trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

python experiments/h-m1/main.py > "$LOG" 2>&1
