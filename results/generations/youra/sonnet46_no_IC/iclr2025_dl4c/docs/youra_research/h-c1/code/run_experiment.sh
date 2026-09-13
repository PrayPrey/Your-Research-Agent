#!/bin/bash
set -e
LOG=/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_dl4c/docs/youra_research/h-c1/code/experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT
source /home/PrayPrey/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-c1
export HUGGING_FACE_HUB_TOKEN="$(cat ~/.cache/huggingface/token)"
export HF_TOKEN="$HUGGING_FACE_HUB_TOKEN"
cd /home/PrayPrey/YouRA_no_IC_sonnet46/TEST_dl4c/docs/youra_research/h-c1/code
python run_scan.py >> "$LOG" 2>&1
