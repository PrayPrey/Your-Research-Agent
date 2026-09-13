#!/bin/bash
# Wait for experiments to complete and generate validation report

LOG="experiment_full.log"
MAX_WAIT=43200  # 12 hours max wait
START=$(date +%s)

echo "Waiting for H-E1 experiments to complete..."
echo "Will check every 60 seconds (max wait: $MAX_WAIT seconds)"

until [ -f "$LOG" ] && grep -q "EXPERIMENT COMPLETE" "$LOG"; do
    ELAPSED=$(($(date +%s) - START))
    if [ $ELAPSED -gt $MAX_WAIT ]; then
        echo "TIMEOUT: Experiments did not complete within $MAX_WAIT seconds"
        exit 1
    fi
    echo "$(date '+%Y-%m-%d %H:%M:%S'): Still running... (elapsed: ${ELAPSED}s)"
    sleep 60
done

echo ""
echo "==================================="
echo "EXPERIMENTS COMPLETED!"
echo "==================================="

# Check completion marker
grep "EXPERIMENT COMPLETE" "$LOG"

# Show results summary
echo ""
echo "==================================="
echo "FINAL RESULTS"
echo "==================================="

if [ -f "outputs/h-e1/results.csv" ]; then
    echo "Results file created successfully"
    wc -l outputs/h-e1/results.csv
    echo ""
    cat outputs/h-e1/results.csv
else
    echo "ERROR: Results file not found!"
    exit 1
fi

# Show validation report
echo ""
echo "==================================="
echo "VALIDATION REPORT"
echo "==================================="

if [ -f "outputs/h-e1/04_validation.md" ]; then
    cat outputs/h-e1/04_validation.md
else
    echo "ERROR: Validation report not found!"
    exit 1
fi

echo ""
echo "==================================="
echo "Phase 4 Complete"
echo "==================================="
