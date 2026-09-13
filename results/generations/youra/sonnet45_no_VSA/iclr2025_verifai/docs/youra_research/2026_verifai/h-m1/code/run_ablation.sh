#!/bin/bash
set -e

# H-M1 Ablation Study Runner
# Validates information gradient hypothesis

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HYPOTHESIS_DIR="$(dirname "$SCRIPT_DIR")"

echo "Starting H-M1 Ablation Study"
echo "Hypothesis: Information gradient - feedback richness scales monotonically"
echo ""

# Setup environment
export HYPOTHESIS_FOLDER="$HYPOTHESIS_DIR"
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "ERROR: ANTHROPIC_API_KEY not set"
    echo "Please set it with: export ANTHROPIC_API_KEY='your-key'"
    exit 1
fi

# Run experiment with completion marker
LOG="${HYPOTHESIS_DIR}/logs/experiment.log"
mkdir -p "$(dirname "$LOG")"

trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

cd "$SCRIPT_DIR"
python -m src.main_ablation "$HYPOTHESIS_DIR" 2>&1 | tee "$LOG"
