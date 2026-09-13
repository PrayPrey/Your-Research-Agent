#!/bin/bash
set -e

cd "$(dirname "$0")"
LOG="experiment.log"

# Completion marker (EXIT trap fires on success, error, OOM, signal)
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

python main.py > "$LOG" 2>&1
