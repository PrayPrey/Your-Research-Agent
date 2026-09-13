#!/bin/bash
set -e
cd "$(dirname "$0")/code"
LOG="../experiment.log"
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT
python run.py > "$LOG" 2>&1
