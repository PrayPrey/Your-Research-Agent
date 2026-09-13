#!/bin/bash
# Monitor H-E1 experiment progress

LOG="experiment_full.log"

echo "==================================="
echo "H-E1 EXPERIMENT PROGRESS MONITOR"
echo "==================================="
echo ""

# Check if experiment is running
if ps aux | grep -E "run_experiments.py" | grep -v grep > /dev/null; then
    echo "✓ Experiment is RUNNING"
else
    echo "✗ Experiment is NOT running"
fi

echo ""
echo "--- Log Statistics ---"
wc -l "$LOG" 2>/dev/null || echo "Log file not found"

echo ""
echo "--- Latest Progress (last 40 lines) ---"
tail -40 "$LOG" 2>/dev/null || echo "Log file not found"

echo ""
echo "--- Experiment Completion Check ---"
if grep -q "EXPERIMENT COMPLETE" "$LOG" 2>/dev/null; then
    echo "✓ Experiment COMPLETED"
    grep "EXPERIMENT COMPLETE" "$LOG"
else
    echo "⏳ Experiment still running..."
fi

echo ""
echo "--- Results Summary (if available) ---"
if [ -f "outputs/h-e1/results.csv" ]; then
    echo "Results file exists:"
    wc -l outputs/h-e1/results.csv
    echo ""
    echo "Latest results:"
    tail -5 outputs/h-e1/results.csv
else
    echo "Results file not yet created"
fi
