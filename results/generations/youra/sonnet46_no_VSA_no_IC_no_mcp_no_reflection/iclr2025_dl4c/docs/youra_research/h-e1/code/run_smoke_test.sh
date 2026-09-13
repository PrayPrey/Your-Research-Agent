#!/bin/bash
# Smoke test: validate GRPOTrainer wiring with real model but 3 steps
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONDA_PY="/home/PrayPrey/miniforge3/envs/youra-h-e1-grpo/bin/python"
LOG="$SCRIPT_DIR/outputs/smoke_test.log"
mkdir -p "$SCRIPT_DIR/outputs"

echo "Smoke test started at $(date -Iseconds)" | tee "$LOG"

CUDA_VISIBLE_DEVICES=0 $CONDA_PY "$SCRIPT_DIR/train.py" \
    --condition binary \
    --steps 3 \
    >> "$LOG" 2>&1
EXIT=$?

echo "EXPERIMENT COMPLETE (exit=$EXIT, ts=$(date -Iseconds))" >> "$LOG"

if [ $EXIT -eq 0 ]; then
    echo "SMOKE TEST PASSED" | tee -a "$LOG"
else
    echo "SMOKE TEST FAILED (exit=$EXIT)" | tee -a "$LOG"
    cat "$LOG"
fi
