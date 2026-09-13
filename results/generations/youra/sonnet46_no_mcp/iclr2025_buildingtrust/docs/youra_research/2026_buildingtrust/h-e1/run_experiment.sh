#!/usr/bin/env bash
set -euo pipefail

CODE_DIR="$(cd "$(dirname "$0")/code" && pwd)"
LOG="$(dirname "$0")/experiment.log"

export CUDA_VISIBLE_DEVICES=0

trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

conda run -n youra-h-e1 python "$CODE_DIR/run_experiment_poc.py" > "$LOG" 2>&1
