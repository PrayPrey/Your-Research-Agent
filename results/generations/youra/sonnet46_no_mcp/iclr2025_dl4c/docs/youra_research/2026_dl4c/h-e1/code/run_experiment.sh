#!/bin/bash
# H-E1 Smoke Test Runner - Phase 4 MUST_WORK validation
# Runs all 4 conditions with --smoke_test flag (10 steps each)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG="$SCRIPT_DIR/experiment.log"

trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

source /home/anonymous/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-e1

export CUDA_VISIBLE_DEVICES=1
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

cd "$SCRIPT_DIR"

echo "============================================================" >> "$LOG"
echo "H-E1 SMOKE TEST EXPERIMENT" >> "$LOG"
echo "Started: $(date -Iseconds)" >> "$LOG"
echo "GPU: $CUDA_VISIBLE_DEVICES" >> "$LOG"
echo "Conda env: youra-h-e1" >> "$LOG"
echo "============================================================" >> "$LOG"

CONDITIONS=("curriculum" "uniform" "easy_only" "hard_only")

for CONDITION in "${CONDITIONS[@]}"; do
    echo "" >> "$LOG"
    echo "--- Condition: $CONDITION ---" >> "$LOG"
    echo "Started: $(date -Iseconds)" >> "$LOG"

    python training/train.py --condition "$CONDITION" --smoke_test >> "$LOG" 2>&1
    EXIT_CODE=$?

    if [ $EXIT_CODE -eq 0 ]; then
        echo "PASSED: $CONDITION (exit=$EXIT_CODE, ts=$(date -Iseconds))" >> "$LOG"
    else
        echo "FAILED: $CONDITION (exit=$EXIT_CODE, ts=$(date -Iseconds))" >> "$LOG"
        exit $EXIT_CODE
    fi
done

echo "" >> "$LOG"
echo "ALL 4 CONDITIONS PASSED SMOKE TEST" >> "$LOG"
echo "Completed: $(date -Iseconds)" >> "$LOG"
