#!/bin/bash
LOG_FILE="experiment_full.log"

# Monitor for experiment completion
tail -f "$LOG_FILE" 2>/dev/null | grep -E --line-buffered "Experiment [0-9]+/15|EXPERIMENT COMPLETE|All experiments finished|Error|Exception|Traceback" | while read line; do
    echo "$line"
    
    # Check if all experiments are complete
    if echo "$line" | grep -q "EXPERIMENT COMPLETE\|All experiments finished"; then
        echo "✓ EXPERIMENTS COMPLETED SUCCESSFULLY"
        exit 0
    fi
    
    # Check for errors
    if echo "$line" | grep -Eq "Error|Exception|Traceback"; then
        echo "✗ ERROR DETECTED IN EXPERIMENTS"
        exit 1
    fi
done
