#!/bin/bash
# Experiment execution wrapper with completion marker

cd "$(dirname "$0")"

LOG="experiment.log"
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

echo "Starting h-e1 experiment at $(date -Iseconds)" | tee "$LOG"

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..." | tee -a "$LOG"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt >> "$LOG" 2>&1
else
    source venv/bin/activate
fi

# Run experiment
echo "Executing experiment..." | tee -a "$LOG"
python main.py >> "$LOG" 2>&1

EXIT_CODE=$?
echo "Experiment finished with exit code $EXIT_CODE at $(date -Iseconds)" | tee -a "$LOG"
exit $EXIT_CODE
