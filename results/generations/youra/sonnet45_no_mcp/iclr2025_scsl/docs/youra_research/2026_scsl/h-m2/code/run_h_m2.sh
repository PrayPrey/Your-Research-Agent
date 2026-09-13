#!/bin/bash
# Run h-m2 experiment with REAL Waterbirds data (MOCK DATA FIX)
# This script fixes the mock data issue detected by external verification

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

LOG="$SCRIPT_DIR/experiment.log"
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

echo "=== H-M2 Experiment: Real Data Execution (MOCK FIX) ===" | tee "$LOG"
echo "Date: $(date)" | tee -a "$LOG"
echo "Directory: $SCRIPT_DIR" | tee -a "$LOG"

# Select GPU with most free memory
if command -v nvidia-smi &> /dev/null; then
    GPU_ID=$(nvidia-smi --query-gpu=index,memory.free --format=csv,noheader,nounits | sort -k2 -nr | head -1 | awk '{print $1}')
    export CUDA_VISIBLE_DEVICES=$GPU_ID
    echo "Using GPU $GPU_ID" | tee -a "$LOG"
else
    export CUDA_VISIBLE_DEVICES=""
    echo "No GPU available, using CPU" | tee -a "$LOG"
fi

# Verify dataset exists
if [ ! -d "data/waterbirds_v1.0" ]; then
    echo "ERROR: Waterbirds dataset not found at data/waterbirds_v1.0" | tee -a "$LOG"
    exit 1
fi

echo "✓ Waterbirds dataset found" | tee -a "$LOG"

# Run h-m2 experiment with timeout (1 hour max)
echo "Running h-m2 experiment with REAL data..." | tee -a "$LOG"
timeout 3600 python run_h_m2_experiment.py 2>&1 | tee -a "$LOG"

echo "Experiment completed" | tee -a "$LOG"
