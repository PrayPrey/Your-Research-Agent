#!/bin/bash
# H-M3 Evaluation: Random Mathlib Tactic Sampling
set -e

LOG=experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

echo "=== H-M3 Evaluation: Random Mathlib Tactic Sampling ===" | tee -a "$LOG"
echo "" | tee -a "$LOG"

# Environment
echo "Environment:" | tee -a "$LOG"
echo "  Lean version: $(lean --version 2>&1 | head -1)" | tee -a "$LOG"
echo "  Workers: 8" | tee -a "$LOG"
echo "  Timeout: 300s per problem" | tee -a "$LOG"
echo "  Tactic budget: 15" | tee -a "$LOG"
echo "" | tee -a "$LOG"

# Use mock miniF2F dataset (50 problems for POC)
MINIF2F_PATH="data/mock_test_244.lean"

if [ ! -f "$MINIF2F_PATH" ]; then
    echo "ERROR: Mock test not found at $MINIF2F_PATH" | tee -a "$LOG"
    exit 1
fi

echo "Using miniF2F from: $MINIF2F_PATH" | tee -a "$LOG"
echo "" | tee -a "$LOG"

# Install Python dependencies
if [ ! -f .venv/bin/activate ]; then
    echo "Creating virtual environment..." | tee -a "$LOG"
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install -q -r requirements.txt

# Run evaluation
echo "Starting evaluation (244 problems)..." | tee -a "$LOG"
start_time=$(date +%s)

python src/main.py \
    --minif2f-path "$MINIF2F_PATH" \
    --config config/tactic_distribution.yaml \
    --budget 15 \
    --timeout 300 \
    --workers 8 \
    --output-dir results \
    --checkpoint-dir checkpoints 2>&1 | tee -a "$LOG"

end_time=$(date +%s)
elapsed=$((end_time - start_time))

echo "" | tee -a "$LOG"
echo "Evaluation complete in ${elapsed}s" | tee -a "$LOG"
echo "" | tee -a "$LOG"

# Statistical analysis
echo "Running statistical analysis..." | tee -a "$LOG"
python src/aggregate.py \
    --results results/h_m3_results.jsonl \
    --output results/h_m3_aggregate.yaml 2>&1 | tee -a "$LOG"

echo "" | tee -a "$LOG"
echo "=== Evaluation Complete ===" | tee -a "$LOG"
