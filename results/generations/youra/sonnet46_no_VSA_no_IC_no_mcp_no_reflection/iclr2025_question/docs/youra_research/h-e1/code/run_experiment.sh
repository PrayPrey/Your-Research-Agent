#!/bin/bash
set -e
CODE_DIR="$(dirname "$(realpath "$0")")"
LOG="$CODE_DIR/experiment.log"
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT
source /home/PrayPrey/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-e1
cd "$CODE_DIR"
python run.py >> "$LOG" 2>&1
