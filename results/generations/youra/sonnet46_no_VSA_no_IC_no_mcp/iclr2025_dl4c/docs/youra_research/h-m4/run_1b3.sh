#!/bin/bash
# 1.3B SFT + RLEF-Fraction training for h-m4
set -euo pipefail

CONDA_PATH=/home/PrayPrey/miniforge3
source "${CONDA_PATH}/etc/profile.d/conda.sh"
conda activate youra-h-m4

export CUDA_VISIBLE_DEVICES=1
export TOKENIZERS_PARALLELISM=false

CODE_DIR="$(cd "$(dirname "$0")/code" && pwd)"
LOG="${CODE_DIR}/experiment_1b3.log"

trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

cd "$CODE_DIR"
python run_experiment.py --track 1b3 >> "$LOG" 2>&1
