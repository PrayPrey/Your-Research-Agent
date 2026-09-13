#!/bin/bash
# H-E1 Experiment Runner: Binary vs Ratio Reward in GRPO
# Runs both conditions in parallel on separate GPUs

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONDA_PY="/home/PrayPrey/miniforge3/envs/youra-h-e1-grpo/bin/python"
LOG_DIR="$SCRIPT_DIR/outputs"
mkdir -p "$LOG_DIR"

echo "=== H-E1 Experiment: Binary vs Ratio Reward ==="
echo "Start: $(date -Iseconds)"
echo "GPUs: $(nvidia-smi --query-gpu=name --format=csv,noheader | wc -l)"

# Run binary condition on GPU 0
LOG_BINARY="$LOG_DIR/train_binary.log"
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG_BINARY"' EXIT

CUDA_VISIBLE_DEVICES=0 $CONDA_PY "$SCRIPT_DIR/train.py" \
    --condition binary \
    > "$LOG_BINARY" 2>&1 &
PID_BINARY=$!
echo "Binary training started (PID=$PID_BINARY)"

# Run ratio condition on GPU 1
LOG_RATIO="$LOG_DIR/train_ratio.log"
CUDA_VISIBLE_DEVICES=1 $CONDA_PY "$SCRIPT_DIR/train.py" \
    --condition ratio \
    > "$LOG_RATIO" 2>&1 &
PID_RATIO=$!
echo "Ratio training started (PID=$PID_RATIO)"

echo "Waiting for both conditions to complete..."
wait "$PID_BINARY"
EXIT_BINARY=$?
echo "Binary done (exit=$EXIT_BINARY)"

wait "$PID_RATIO"
EXIT_RATIO=$?
echo "Ratio done (exit=$EXIT_RATIO)"

echo "Training complete at $(date -Iseconds)"

# Evaluate HumanEval checkpoints
if [ $EXIT_BINARY -eq 0 ] && [ -d "$SCRIPT_DIR/outputs/checkpoints/binary/checkpoint-200" ]; then
    echo "Evaluating binary condition on HumanEval..."
    CUDA_VISIBLE_DEVICES=0 $CONDA_PY "$SCRIPT_DIR/evaluate.py" \
        --condition binary \
        > "$LOG_DIR/eval_binary.log" 2>&1 &
    PID_EVAL_BINARY=$!
fi

if [ $EXIT_RATIO -eq 0 ] && [ -d "$SCRIPT_DIR/outputs/checkpoints/ratio/checkpoint-200" ]; then
    echo "Evaluating ratio condition on HumanEval..."
    CUDA_VISIBLE_DEVICES=1 $CONDA_PY "$SCRIPT_DIR/evaluate.py" \
        --condition ratio \
        > "$LOG_DIR/eval_ratio.log" 2>&1 &
    PID_EVAL_RATIO=$!
fi

[ -n "$PID_EVAL_BINARY" ] && wait "$PID_EVAL_BINARY"; echo "Binary eval done"
[ -n "$PID_EVAL_RATIO" ] && wait "$PID_EVAL_RATIO"; echo "Ratio eval done"

# Analysis
echo "Running analysis..."
$CONDA_PY "$SCRIPT_DIR/analyze.py" > "$LOG_DIR/analyze.log" 2>&1

echo "=== Experiment Complete: $(date -Iseconds) ==="
echo "EXPERIMENT COMPLETE (exit=0, ts=$(date -Iseconds))"
