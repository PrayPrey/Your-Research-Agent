#!/bin/bash
export CUDA_VISIBLE_DEVICES=4
export HF_HOME=/home/PrayPrey/.cache/huggingface
LOG=/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_scope/docs/youra_research/h-e1/experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT
cd /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_scope/docs/youra_research/h-e1
/home/PrayPrey/miniforge3/envs/h-m1-exp/bin/python run_experiment.py > "$LOG" 2>&1
