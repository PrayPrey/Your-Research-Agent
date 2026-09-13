#!/bin/bash
LOG=experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT
python src/main.py 2>&1 | tee "$LOG"
