#!/bin/bash
# H-M2: Run RLEF training via SimpleGRPOTrainer to generate reward_monitoring.jsonl
# This generates the log that analyze_reward_fractions.py reads.

H_E1_CODE="/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_dl4c/docs/youra_research/h-e1/code"
LOG="$H_E1_CODE/experiment_hm2_rlef.log"

trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

source /home/PrayPrey/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-e1

cd "$H_E1_CODE"
python train_rlef.py config.yaml > "$LOG" 2>&1
