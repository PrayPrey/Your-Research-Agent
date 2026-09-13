#!/bin/bash
set -euo pipefail
CODE_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG="$CODE_DIR/experiment.log"

trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

source /home/PrayPrey/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-e1

cd "$CODE_DIR"
python -u run.py > "$LOG" 2>&1
