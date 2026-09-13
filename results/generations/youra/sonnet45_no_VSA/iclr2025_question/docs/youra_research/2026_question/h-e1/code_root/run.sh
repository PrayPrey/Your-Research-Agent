#!/bin/bash
set -euo pipefail

LOG="code/h-e1/experiment.log"
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

cd code/h-e1
python main.py 2>&1 | tee "$LOG"
