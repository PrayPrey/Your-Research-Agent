#!/bin/bash
set -e

LOG="experiment.log"
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

echo "=== H-E1 Experiment Pipeline ===" | tee "$LOG"
echo "Start: $(date -Iseconds)" | tee -a "$LOG"

# Step 1: Generate synthetic validation data
echo -e "\n[1/3] Generating synthetic validation data..." | tee -a "$LOG"
python3 scripts/generate_synthetic_validation_data.py >> "$LOG" 2>&1

# Step 2: Compute inter-rater reliability
echo -e "\n[2/3] Computing inter-rater reliability..." | tee -a "$LOG"
python3 scripts/compute_reliability.py \
  --ratings data/benchmark_metadata_corpus/ground_truth_labels.csv \
  --output outputs/inter_rater_reliability.json >> "$LOG" 2>&1

# Step 3: Verify corpus gate conditions
echo -e "\n[3/3] Verifying corpus..." | tee -a "$LOG"
python3 scripts/verify_corpus.py \
  --corpus data/benchmark_metadata_corpus/ \
  --ratings data/benchmark_metadata_corpus/ground_truth_labels.csv \
  --reliability outputs/inter_rater_reliability.json \
  --output outputs/verification_result.json >> "$LOG" 2>&1

echo -e "\nExperiment complete: $(date -Iseconds)" | tee -a "$LOG"
echo "Results saved to outputs/" | tee -a "$LOG"
