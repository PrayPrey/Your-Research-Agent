#!/bin/bash
# h-e1 full experiment: llama2 (donor+fresh) -> mistral -> llama3 -> analyze -> heatmap
cd "$(dirname "$0")"
source /home/PrayPrey/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-e1-v2
export CUDA_VISIBLE_DEVICES=2

LOG=experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

{
  echo "=== h-e1 full experiment started $(date -Iseconds) ==="
  python run_h_e1.py --model llama2 --full &&
  python run_h_e1.py --model mistral --full &&
  python run_h_e1.py --model llama3 --full &&
  python run_h_e1.py --model all --analyze &&
  python generate_figures.py
  echo "=== chain finished $(date -Iseconds) ==="
} > "$LOG" 2>&1
