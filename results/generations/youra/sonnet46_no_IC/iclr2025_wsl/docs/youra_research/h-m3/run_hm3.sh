#!/bin/bash
set -e
cd "$(dirname "$0")"
source /home/PrayPrey/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-m3

export PROJECT_ROOT=/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_wsl

LOG=experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

python run_hm3.py "$@" > "$LOG" 2>&1
