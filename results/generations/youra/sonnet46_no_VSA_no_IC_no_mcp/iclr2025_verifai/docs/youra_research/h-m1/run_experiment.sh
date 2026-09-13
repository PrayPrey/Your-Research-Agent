#!/bin/bash
set -euo pipefail
LOG=docs/youra_research/h-m1/experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

cd /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_verifai
source .env 2>/dev/null || true

python docs/youra_research/h-m1/code/run.py > "$LOG" 2>&1
