#!/bin/bash

# Simple progress checker for H-E2 experiment

LOG="experiment.log"

if [ ! -f "$LOG" ]; then
    echo "Experiment log not found - experiment may not have started"
    exit 1
fi

echo "=== Experiment Progress ==="
echo ""

# Check if experiment completed
if grep -q "EXPERIMENT COMPLETE" "$LOG"; then
    echo "STATUS: COMPLETED"
    grep "EXPERIMENT COMPLETE" "$LOG"
    echo ""
fi

# Show phase progress
echo "Phase Progress:"
grep -E "Phase [0-9]:" "$LOG" | tail -5 || echo "  No phase markers yet"
echo ""

# Show config progress
CONFIG_COUNT=$(grep -c "Running config:" "$LOG" 2>/dev/null)
echo "Configs Profiled: $CONFIG_COUNT"

# Show latest config results
echo ""
echo "Latest Results:"
grep -E "SAT=|degradation=" "$LOG" | tail -3 || echo "  No results yet"

# Show gate status if available
echo ""
if grep -q "Gate Status:" "$LOG"; then
    echo "Gate Validation:"
    grep -A 3 "Gate Status:" "$LOG" | tail -4
fi

# Show last few log lines
echo ""
echo "Recent Activity:"
tail -5 "$LOG"
