#!/bin/bash
set -e

LOG=experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

cd "$(dirname "$0")"
python main.py 2>&1 | tee "$LOG"
