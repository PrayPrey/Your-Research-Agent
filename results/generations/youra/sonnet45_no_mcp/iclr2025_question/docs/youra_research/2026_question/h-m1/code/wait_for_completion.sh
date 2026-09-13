#!/bin/bash
echo "Waiting for experiment to complete..."
echo "Started at: $(date)"
echo "Process PID: 2325280"
echo ""

while ps -p 2325280 > /dev/null 2>&1; do
    ELAPSED=$(ps -p 2325280 -o etime= | tr -d ' ')
    GPU_UTIL=$(nvidia-smi --query-gpu=index,utilization.gpu --format=csv,noheader,nounits | head -1 | cut -d',' -f2 | tr -d ' ')
    echo "[$(date +%H:%M:%S)] Still running... Elapsed: $ELAPSED, GPU: ${GPU_UTIL}%"
    sleep 60
done

echo ""
echo "Process completed at: $(date)"
if [ -f outputs/correlation_results.json ]; then
    echo "✅ SUCCESS: Results file created"
    echo "File size: $(ls -lh outputs/correlation_results.json | awk '{print $5}')"
else
    echo "❌ ERROR: Results file not found"
fi
