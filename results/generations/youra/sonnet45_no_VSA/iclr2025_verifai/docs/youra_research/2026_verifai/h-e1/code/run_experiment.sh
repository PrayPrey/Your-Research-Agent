#!/bin/bash
# H-E1 Experiment Runner with completion marker

set -e

# Experiment configuration
LOG="docs/youra_research/h-e1/code/results/experiment.log"
CONFIG="docs/youra_research/h-e1/code/config/experiment_config.yaml"

# Create log directory
mkdir -p "$(dirname "$LOG")"

# Install completion marker as first action
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

# Check environment
echo "Checking environment..." | tee -a "$LOG"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found" | tee -a "$LOG"
    exit 1
fi

# Check Frama-C
if ! command -v frama-c &> /dev/null; then
    echo "WARNING: Frama-C not found. Install with: opam install frama-c" | tee -a "$LOG"
    echo "Experiment will use fallback programs only." | tee -a "$LOG"
fi

# Check API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "ERROR: ANTHROPIC_API_KEY not set" | tee -a "$LOG"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..." | tee -a "$LOG"
cd docs/youra_research/h-e1/code
pip install -q -r requirements.txt

# Run experiment
echo "Starting experiment..." | tee -a "$LOG"
echo "Configuration: $CONFIG" | tee -a "$LOG"
echo "Log file: $LOG" | tee -a "$LOG"
echo "" | tee -a "$LOG"

python3 -m src.main "$CONFIG" 2>&1 | tee -a "$LOG"

echo "" | tee -a "$LOG"
echo "Experiment finished. Check results in docs/youra_research/h-e1/code/results/" | tee -a "$LOG"
