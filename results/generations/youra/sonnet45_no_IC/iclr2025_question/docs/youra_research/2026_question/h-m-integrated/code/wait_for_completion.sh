#!/bin/bash
# Wait for experiment completion with progress monitoring

LOG_FILE="experiment.log"
TIMEOUT=7200  # 2 hours max
START_TIME=$(date +%s)

echo "Monitoring experiment progress..."
echo "Log file: $LOG_FILE"
echo "Timeout: ${TIMEOUT}s ($(($TIMEOUT/60)) minutes)"
echo ""

# Wait for completion marker or timeout
while true; do
    ELAPSED=$(($(date +%s) - START_TIME))

    # Check for completion marker
    if [ -f "$LOG_FILE" ] && grep -q "EXPERIMENT COMPLETE" "$LOG_FILE"; then
        echo "✅ Experiment completed successfully!"
        tail -30 "$LOG_FILE"
        exit 0
    fi

    # Check for timeout
    if [ $ELAPSED -gt $TIMEOUT ]; then
        echo "❌ Timeout reached (${TIMEOUT}s)"
        echo "Last 50 lines of log:"
        tail -50 "$LOG_FILE" 2>/dev/null || echo "No log file"
        exit 1
    fi

    # Progress update every 60s
    if [ $(($ELAPSED % 60)) -eq 0 ]; then
        MINUTES=$(($ELAPSED / 60))
        echo "[$MINUTES min] Still running... (last 3 lines):"
        tail -3 "$LOG_FILE" 2>/dev/null || echo "  (waiting for log output)"
    fi

    sleep 5
done
