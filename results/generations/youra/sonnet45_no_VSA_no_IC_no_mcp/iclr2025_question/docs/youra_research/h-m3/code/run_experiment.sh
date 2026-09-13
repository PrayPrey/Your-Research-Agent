#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

LOG=experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

echo "Installing dependencies..." > "$LOG" 2>&1
pip install -q -r requirements.txt >> "$LOG" 2>&1

echo "Running H-M3 viability classification experiment..." >> "$LOG" 2>&1
python main.py >> "$LOG" 2>&1

echo "Experiment finished successfully." >> "$LOG" 2>&1
