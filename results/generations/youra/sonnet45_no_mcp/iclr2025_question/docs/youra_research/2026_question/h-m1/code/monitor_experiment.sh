#!/bin/bash
while true; do
    if [ -f outputs/correlation_results.json ]; then
        echo "✅ Experiment completed at $(date)"
        echo "Results file size: $(ls -lh outputs/correlation_results.json | awk '{print $5}')"
        exit 0
    fi
    
    if ! ps -p 2325280 > /dev/null 2>&1; then
        echo "❌ Process stopped unexpectedly at $(date)"
        exit 1
    fi
    
    sleep 30
done
