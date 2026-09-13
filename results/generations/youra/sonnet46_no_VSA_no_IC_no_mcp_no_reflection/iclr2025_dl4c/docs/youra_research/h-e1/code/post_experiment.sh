#!/bin/bash
# Post-experiment: evaluate HumanEval and run analysis
# Run after training completes

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONDA_PY="/home/PrayPrey/miniforge3/envs/youra-h-e1-grpo/bin/python"
LOG_DIR="$SCRIPT_DIR/outputs"

echo "=== Post-Experiment Evaluation ==="
echo "Start: $(date -Iseconds)"

# Evaluate both conditions in parallel
LOG_EVAL_B="$LOG_DIR/eval_binary.log"
LOG_EVAL_R="$LOG_DIR/eval_ratio.log"

CUDA_VISIBLE_DEVICES=0 $CONDA_PY "$SCRIPT_DIR/evaluate.py" \
    --condition binary \
    > "$LOG_EVAL_B" 2>&1 &
PID_EB=$!

CUDA_VISIBLE_DEVICES=1 $CONDA_PY "$SCRIPT_DIR/evaluate.py" \
    --condition ratio \
    > "$LOG_EVAL_R" 2>&1 &
PID_ER=$!

wait "$PID_EB"; echo "Binary eval done (exit=$?)"
wait "$PID_ER"; echo "Ratio eval done (exit=$?)"

# Run analysis
$CONDA_PY "$SCRIPT_DIR/analyze.py" 2>&1 | tee "$LOG_DIR/analyze.log"

echo "=== Post-Experiment Complete: $(date -Iseconds) ==="
