#!/bin/bash
# Fast experiment: 150 steps, enough for bootstrap CI (steps 100-150)
# Uses GPUs 0 and 1 (free after previous stale run cleared)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONDA_PY="/home/PrayPrey/miniforge3/envs/youra-h-e1-grpo/bin/python"
LOG_DIR="$SCRIPT_DIR/outputs"
mkdir -p "$LOG_DIR"

# Clear old (header-only) CSV files from failed run
> "$LOG_DIR/gradient_norms_binary.csv"
> "$LOG_DIR/gradient_norms_ratio.csv"

echo "=== H-E1 Fast Experiment: Binary vs Ratio Reward (150 steps) ==="
echo "Start: $(date -Iseconds)"

LOG_BINARY="$LOG_DIR/train_binary.log"
LOG_RATIO="$LOG_DIR/train_ratio.log"

CUDA_VISIBLE_DEVICES=0 $CONDA_PY "$SCRIPT_DIR/train.py" \
    --condition binary \
    --steps 150 \
    > "$LOG_BINARY" 2>&1 &
PID_BINARY=$!
echo "Binary training started (PID=$PID_BINARY, GPU=0)"

CUDA_VISIBLE_DEVICES=1 $CONDA_PY "$SCRIPT_DIR/train.py" \
    --condition ratio \
    --steps 150 \
    > "$LOG_RATIO" 2>&1 &
PID_RATIO=$!
echo "Ratio training started (PID=$PID_RATIO, GPU=1)"

echo "Waiting for both conditions..."
wait "$PID_BINARY"
EXIT_BINARY=$?
echo "Binary done (exit=$EXIT_BINARY, $(date -Iseconds))"

wait "$PID_RATIO"
EXIT_RATIO=$?
echo "Ratio done (exit=$EXIT_RATIO, $(date -Iseconds))"

if [ $EXIT_BINARY -ne 0 ] || [ $EXIT_RATIO -ne 0 ]; then
    echo "ERROR: one or both conditions failed"
    exit 1
fi

echo "Running analysis..."
$CONDA_PY "$SCRIPT_DIR/analyze.py" > "$LOG_DIR/analyze.log" 2>&1
echo "Analysis done. Results:"
cat "$LOG_DIR/analyze.log"

echo "=== Experiment Complete: $(date -Iseconds) ==="
