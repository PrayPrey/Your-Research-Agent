#!/bin/bash
cd /home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_verifai/docs/youra_research/h-m3
LOG=experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT
python3 code/run_experiment.py > "$LOG" 2>&1
