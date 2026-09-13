#!/bin/bash
cd /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/opus45/TEST_data_problems/docs/youra_research/h-e1/code
LOG=experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT
python train.py > "$LOG" 2>&1
