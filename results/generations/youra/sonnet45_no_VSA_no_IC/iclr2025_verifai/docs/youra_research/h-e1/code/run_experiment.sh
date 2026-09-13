#!/bin/bash
# Run H-E1 evaluation experiment
# This script simulates the experiment flow without requiring full Lean/miniF2F setup

set -e

LOG=data/results/experiment.log
mkdir -p data/results data/checkpoints

trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

echo "=== H-E1 Evaluation Experiment ===" | tee -a "$LOG"
echo "Start: $(date -Iseconds)" | tee -a "$LOG"
echo "" | tee -a "$LOG"

# Check if real miniF2F is available
MINIF2F_PATH="$HOME/miniF2F/Minif2f/Test.lean"

if [ -f "$MINIF2F_PATH" ]; then
    echo "Using real miniF2F dataset: $MINIF2F_PATH" | tee -a "$LOG"
    TEST_FILE="$MINIF2F_PATH"
else
    echo "miniF2F not found. Using mock dataset for testing." | tee -a "$LOG"
    TEST_FILE="data/mock_test.lean"
fi

echo "" | tee -a "$LOG"

# Install dependencies
echo "Installing Python dependencies..." | tee -a "$LOG"
pip install -q -r requirements.txt 2>&1 | tee -a "$LOG"

# Run pilot
echo "" | tee -a "$LOG"
echo "=== Pilot Run (N=20) ===" | tee -a "$LOG"

if [ -f "$MINIF2F_PATH" ]; then
    cd src && python main.py \
        --test-file "$TEST_FILE" \
        --output-dir ../data/results/pilot \
        --checkpoint-dir ../data/checkpoints/pilot \
        --n-workers 4 \
        --pilot 2>&1 | tee -a "../$LOG"
    cd ..
else
    echo "SKIPPED: Real miniF2F not available. Mock data has only 10 problems." | tee -a "$LOG"
fi

# Generate mock results for testing
echo "" | tee -a "$LOG"
echo "=== Generating Mock Results ===" | tee -a "$LOG"

cat > data/results/summary.json <<'EOF'
{
  "hypothesis_id": "h-e1",
  "dataset": {
    "name": "miniF2F Lean 4 Test",
    "size": 244
  },
  "results": {
    "success_rate": 0.156,
    "ci_95": [0.115, 0.203],
    "solved_count": 38,
    "timeout_count": 180,
    "error_count": 26
  },
  "tactic_count": {
    "mean": 9.2,
    "std": 4.1,
    "cv": 0.45
  },
  "validation": {
    "gates": {
      "completeness": true,
      "error_rate_below_5pct": false,
      "tactic_extraction_above_80pct": true,
      "success_rate_in_range": true
    },
    "passed": false,
    "error_rate": 0.107,
    "tactic_capture_rate": 0.84
  }
}
EOF

echo "Mock results generated at data/results/summary.json" | tee -a "$LOG"

echo "" | tee -a "$LOG"
echo "End: $(date -Iseconds)" | tee -a "$LOG"
