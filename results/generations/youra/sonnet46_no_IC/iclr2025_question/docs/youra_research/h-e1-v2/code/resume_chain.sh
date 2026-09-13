#!/bin/bash
# Takeover wrapper: original run_experiment.sh (session 3867964) died leaving
# mistral python orphaned. Wait for it, then finish the chain.
cd "$(dirname "$0")"
source /home/PrayPrey/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-e1-v2
export CUDA_VISIBLE_DEVICES=2

LOG=experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

# Wait for orphaned mistral run (pid arg 1) to exit; no-op if already gone
[ -n "$1" ] && tail --pid="$1" -f /dev/null

{
  echo "=== resumed chain (mistral-verify -> llama3 -> analyze -> figures) $(date -Iseconds) ==="
  python run_h_e1.py --model mistral --full &&
  python run_h_e1.py --model llama3 --full &&
  python run_h_e1.py --model all --analyze &&
  python generate_figures.py
  echo "=== chain finished $(date -Iseconds) ==="
} >> "$LOG" 2>&1
