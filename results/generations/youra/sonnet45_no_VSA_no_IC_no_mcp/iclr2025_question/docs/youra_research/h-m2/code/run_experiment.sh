#!/bin/bash
# H-M2 Bayesian Gate 2 validation experiment

set -e

LOG=experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

echo "=== H-M2 Bayesian Gate 2 Validation ===" | tee "$LOG"
echo "Started: $(date -Iseconds)" | tee -a "$LOG"

# Install dependencies
echo "" | tee -a "$LOG"
echo "Installing dependencies..." | tee -a "$LOG"
pip install -q -r requirements.txt 2>&1 | tee -a "$LOG"

# Run validation
echo "" | tee -a "$LOG"
echo "Running validation pipeline..." | tee -a "$LOG"
python main.py --output-dir .. 2>&1 | tee -a "$LOG"

echo "" | tee -a "$LOG"
echo "Validation complete: $(date -Iseconds)" | tee -a "$LOG"
