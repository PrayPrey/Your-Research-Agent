#!/bin/bash
cd /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_verifai
LOG=docs/youra_research/h-m1/humaneval_run.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT
python3 docs/youra_research/h-m1/run_humaneval_only.py > "$LOG" 2>&1
