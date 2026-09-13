#!/bin/bash
# Main experiment runner for h-m2

set -e
cd "$(dirname "$0")/.."

LOG=experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

echo "Starting h-m2 experiment..." | tee -a "$LOG"

# Step 1: Prepare data
echo "Step 1: Preparing Dolly splits..." | tee -a "$LOG"
python code/prepare_data.py 2>&1 | tee -a "$LOG"

# Step 2: Create variants
echo "Step 2: Creating dataset variants..." | tee -a "$LOG"
python code/create_variants.py 2>&1 | tee -a "$LOG"

# Step 3: Train models (PoC: mock training)
echo "Step 3: Training models (SKIPPED - PoC mode)..." | tee -a "$LOG"
echo "In PoC mode, evaluation uses mock scores." | tee -a "$LOG"

# Step 4: Evaluate
echo "Step 4: Evaluating models (mock)..." | tee -a "$LOG"
python code/evaluate.py 2>&1 | tee -a "$LOG"

# Step 5: Statistical analysis
echo "Step 5: Computing deltas and statistics..." | tee -a "$LOG"
python code/analyze.py 2>&1 | tee -a "$LOG"

# Step 6: Gate check
echo "Step 6: Running gate check..." | tee -a "$LOG"
python code/gate_check.py 2>&1 | tee -a "$LOG"

echo "Experiment complete. Check results/ for outputs." | tee -a "$LOG"
