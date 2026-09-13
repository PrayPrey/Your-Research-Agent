#!/bin/bash
# Check if experiment has completed and results exist

RESULTS_FILE="code/results/h_e1_results.md"
LOG_FILE="code/logs/experiment_log.txt"

if [ -f "$RESULTS_FILE" ]; then
    echo "COMPLETED: Results file exists"
    grep -E "FINAL DECISION|Validation Accuracy" "$LOG_FILE" 2>/dev/null || echo "No decision found in log"
    exit 0
else
    echo "RUNNING: Results file not yet created"
    tail -1 "$LOG_FILE" 2>/dev/null || echo "No log file"
    exit 1
fi
