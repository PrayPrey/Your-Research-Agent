#!/usr/bin/env bash
# run_experiment.sh — H-M3 experiment launcher

set -e

LOG=experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

source /home/PrayPrey/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-m3

echo "[$(date -Iseconds)] Starting H-M3 experiment" | tee "$LOG"

python run_experiment.py 2>&1 | tee -a "$LOG"
