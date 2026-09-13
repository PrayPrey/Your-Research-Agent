#!/bin/bash
set -euo pipefail

CONDA_PATH="/home/PrayPrey/miniforge3"
CODE_DIR="/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet46/TEST_dl4c/docs/youra_research/h-m1/code"
CONDITION="$1"
LOG="${CODE_DIR}/outputs/train_${CONDITION}.log"

trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

source $CONDA_PATH/etc/profile.d/conda.sh

cd "$CODE_DIR"

echo "=== H-M1 Training: condition=$CONDITION ===" >> "$LOG"
echo "Started: $(date -Iseconds)" >> "$LOG"

conda run -n youra-h-m1 python train.py --condition "$CONDITION" --steps 1000 >> "$LOG" 2>&1

