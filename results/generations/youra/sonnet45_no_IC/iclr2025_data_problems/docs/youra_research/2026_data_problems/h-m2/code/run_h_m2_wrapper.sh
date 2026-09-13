#!/bin/bash
# H-M2 Experiment Wrapper with completion marker

cd "$(dirname "$0")"
LOG=experiment.log

# Install completion marker finalizer (MANDATORY)
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

echo "Starting H-M2 experiment at $(date -Iseconds)" > "$LOG"
echo "======================================" >> "$LOG"

# Run experiment with timeout (4 hours = 14400 seconds)
timeout 14400 conda run -n youra-h-m2 --no-capture-output python run_h_m2_experiment.py >> "$LOG" 2>&1

EXIT_CODE=$?
echo "======================================" >> "$LOG"
echo "Experiment finished with exit code: $EXIT_CODE at $(date -Iseconds)" >> "$LOG"

exit $EXIT_CODE
