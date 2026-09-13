#!/bin/bash
# Full 5000-step H-E1 training launcher for H-M1 log generation
# Run from: docs/youra_research/20260502_dl4c/

set -e
RESEARCH_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$RESEARCH_DIR"

export CUDA_VISIBLE_DEVICES=1

source /home/anonymous/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-e1

mkdir -p h-e1/logs

LOG=h-m1/code/experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

echo "Starting H-E1 full training for H-M1 log generation" | tee "$LOG"
echo "Date: $(date -Iseconds)" | tee -a "$LOG"
echo "CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES" | tee -a "$LOG"

for CONDITION in curriculum uniform easy_only hard_only; do
    echo "" | tee -a "$LOG"
    echo "=== Training condition: $CONDITION ===" | tee -a "$LOG"
    echo "Started: $(date -Iseconds)" | tee -a "$LOG"

    python h-e1/code/training/train.py --condition "$CONDITION" >> "$LOG" 2>&1
    RC=$?
    echo "Condition $CONDITION exit=$RC at $(date -Iseconds)" | tee -a "$LOG"

    if [ $RC -ne 0 ]; then
        echo "ERROR: Training failed for condition $CONDITION (exit=$RC)" | tee -a "$LOG"
        exit $RC
    fi

    # Verify log produced
    CSV="h-e1/logs/reward_density_${CONDITION}.csv"
    if [ -f "$CSV" ]; then
        ROWS=$(wc -l < "$CSV")
        echo "Log rows for $CONDITION: $ROWS" | tee -a "$LOG"
    else
        echo "WARNING: CSV not found: $CSV" | tee -a "$LOG"
    fi
done

echo "" | tee -a "$LOG"
echo "All 4 conditions complete at $(date -Iseconds)" | tee -a "$LOG"
