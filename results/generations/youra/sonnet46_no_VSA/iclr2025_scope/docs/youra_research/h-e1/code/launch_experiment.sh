#!/usr/bin/env bash
export HF_HOME="/home/PrayPrey/.cache/huggingface"
export HF_DATASETS_CACHE="${HF_HOME}/datasets"
CODE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG="$CODE_DIR/experiment.log"
CONDA_PYTHON="/home/PrayPrey/miniforge3/envs/youra-h-e1/bin/python"

trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

{
  echo "=== H-E1 Experiment Start: $(date -Iseconds) PID:$$ GPU:$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | wc -l) ==="
  cd "$CODE_DIR"
  "$CONDA_PYTHON" run_experiment.py
} >> "$LOG" 2>&1
