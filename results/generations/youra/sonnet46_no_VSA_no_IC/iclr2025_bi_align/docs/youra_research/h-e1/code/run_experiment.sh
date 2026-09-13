#!/bin/bash
set -e
CODEDIR="$(cd "$(dirname "$0")" && pwd)"
LOG="$CODEDIR/experiment.log"
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

source /home/PrayPrey/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-e1

cd "$CODEDIR"
python run_h_e1.py >> "$LOG" 2>&1
