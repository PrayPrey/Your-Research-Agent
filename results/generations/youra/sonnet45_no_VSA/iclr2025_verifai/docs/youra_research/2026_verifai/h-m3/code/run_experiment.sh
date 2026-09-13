#!/bin/bash
set -e

# H-M3 Cross-Verifier Transfer Experiment Runner
# This script runs the full experiment and generates validation report

LOG="experiment.log"
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

echo "=== H-M3 Cross-Verifier Transfer Experiment ===" | tee "$LOG"
echo "Start time: $(date -Iseconds)" | tee -a "$LOG"
echo "" | tee -a "$LOG"

# Change to code directory
cd "$(dirname "$0")"

# Install dependencies (if needed)
if ! python3 -c "import numpy, pandas, matplotlib" 2>/dev/null; then
    echo "Installing dependencies..." | tee -a "$LOG"
    pip install -q -r requirements.txt >> "$LOG" 2>&1
fi

# Run experiment
echo "Running cross-verifier transfer experiment..." | tee -a "$LOG"
python3 src/main.py 2>&1 | tee -a "$LOG"

EXIT_CODE=${PIPESTATUS[0]}

echo "" | tee -a "$LOG"
echo "Exit code: $EXIT_CODE" | tee -a "$LOG"
echo "End time: $(date -Iseconds)" | tee -a "$LOG"

if [ $EXIT_CODE -eq 0 ]; then
    echo "✓ Experiment completed successfully" | tee -a "$LOG"
else
    echo "✗ Experiment failed with code $EXIT_CODE" | tee -a "$LOG"
fi

exit $EXIT_CODE
