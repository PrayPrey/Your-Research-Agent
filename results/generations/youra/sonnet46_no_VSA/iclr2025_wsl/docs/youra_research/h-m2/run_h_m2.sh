#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG="$SCRIPT_DIR/experiment.log"
> "$LOG"

trap 'echo "EXPERIMENT COMPLETE (exit=$?)" >> "$LOG"' EXIT

echo "[$(date)] Starting H-M2 experiment" | tee -a "$LOG"

source /home/PrayPrey/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-m2

timeout 3600 python "$SCRIPT_DIR/code/run_experiment.py" 2>&1 | tee -a "$LOG"
