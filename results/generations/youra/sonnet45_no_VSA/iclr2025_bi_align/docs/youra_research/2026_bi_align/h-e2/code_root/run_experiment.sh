#!/bin/bash
set -e

cd /workspace/TEST_bi_align

LOG=experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

python experiments/run_evaluation.py > "$LOG" 2>&1
