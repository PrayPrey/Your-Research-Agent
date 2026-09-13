#!/bin/bash
# Launcher for h-e1 full experiment run (10 seeds)

set -e

LOG=experiment_full.log

# Completion marker trap (MANDATORY - prevents unrecoverable hangs)
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

echo "Starting h-e1 full experiment run (10 seeds, CMNIST only)" | tee -a "$LOG"
echo "Start time: $(date -Iseconds)" | tee -a "$LOG"

python3 main.py 2>&1 | tee -a "$LOG"

echo "Experiment completed successfully" | tee -a "$LOG"
