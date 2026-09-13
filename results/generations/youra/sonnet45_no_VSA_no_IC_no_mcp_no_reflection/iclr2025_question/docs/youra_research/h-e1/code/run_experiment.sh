#!/bin/bash
cd /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet45/TEST_question/docs/youra_research/h-e1/code
source venv/bin/activate

LOG=experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

python main.py 2>&1 | tee -a "$LOG"
