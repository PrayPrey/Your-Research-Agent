#!/bin/bash
LOG=/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_wsl/docs/youra_research/h-m1/experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT
cd /home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_wsl/docs/youra_research/h-m1/code
/home/PrayPrey/miniforge3/envs/youra-h-e1/bin/python run_experiment.py > "$LOG" 2>&1
