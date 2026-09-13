#!/bin/bash
cd "$(dirname "$0")"
LOG=experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT
python main.py > "$LOG" 2>&1
