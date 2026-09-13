#!/bin/bash

set -e

cd "$(dirname "$0")"

LOG="outputs/experiment_execution.log"
mkdir -p outputs

# MANDATORY: Install completion-marker finalizer FIRST
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

echo "Starting h-e1 smoke test experiment at $(date -Iseconds)" | tee -a "$LOG"
echo "========================================" | tee -a "$LOG"

python3 h_e1_smoke_test.py 2>&1 | tee -a "$LOG"

EXIT_CODE=${PIPESTATUS[0]}

echo "========================================" | tee -a "$LOG"
echo "Experiment finished at $(date -Iseconds) with exit code $EXIT_CODE" | tee -a "$LOG"

exit $EXIT_CODE
