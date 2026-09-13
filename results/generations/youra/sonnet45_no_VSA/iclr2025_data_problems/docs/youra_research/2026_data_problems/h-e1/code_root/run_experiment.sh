#!/bin/bash
set -e

LOG=logs/experiment.log
mkdir -p logs

# Completion marker finalizer (MANDATORY)
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

echo "Starting H-E1 Static Coupling Metrics Extraction Experiment"
echo "Timestamp: $(date -Iseconds)"
echo ""

# Run experiment
python main.py 2>&1 | tee "$LOG"

echo ""
echo "Experiment finished"
echo "Results saved to: results/"
echo "Figures saved to: figures/"
echo "Log saved to: $LOG"
