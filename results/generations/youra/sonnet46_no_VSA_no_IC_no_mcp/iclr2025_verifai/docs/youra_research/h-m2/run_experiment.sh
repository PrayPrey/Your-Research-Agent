#!/bin/bash
set -euo pipefail
LOG=docs/youra_research/h-m2/experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

cd /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_verifai

# Strip \r from API key (Windows-style .env)
OKEY=$(grep OPENAI_API_KEY .env | cut -d= -f2- | tr -d '\r')

conda run --no-capture-output -n youra-h-m2 env OPENAI_API_KEY="$OKEY" python docs/youra_research/h-m2/code/run.py >> "$LOG" 2>&1
