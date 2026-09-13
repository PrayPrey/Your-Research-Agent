#!/bin/bash
set -euo pipefail
LOG=/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet46/TEST_scope/docs/youra_research/h-e1/experiment4.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT
source /home/PrayPrey/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-e1
cd /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet46/TEST_scope/docs/youra_research/h-e1/code
python run_experiment_v4.py > "$LOG" 2>&1
