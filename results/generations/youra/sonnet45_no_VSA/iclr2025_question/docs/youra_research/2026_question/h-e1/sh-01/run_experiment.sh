#!/bin/bash
# Experiment launcher for sh-01 with completion marker

set -e

cd "$(dirname "$0")"

LOG="experiment.log"

# MANDATORY: Install completion marker finalizer FIRST
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

# Run experiment
echo "Starting sh-01 experiment at $(date -Iseconds)" > "$LOG"
echo "Using mock mode (no API key required)" >> "$LOG"

python main_mock.py >> "$LOG" 2>&1

echo "Experiment finished successfully at $(date -Iseconds)" >> "$LOG"
