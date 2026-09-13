#!/bin/bash
# H-E1 experiment launcher — runs all lm-eval evaluations sequentially
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG="$SCRIPT_DIR/../experiment.log"

trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

source /home/PrayPrey/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-e1

cd "$SCRIPT_DIR"

echo "=== H-E1 Experiment Start: $(date -Iseconds) ===" | tee -a "$LOG"

python main.py 2>&1 | tee -a "$LOG"
