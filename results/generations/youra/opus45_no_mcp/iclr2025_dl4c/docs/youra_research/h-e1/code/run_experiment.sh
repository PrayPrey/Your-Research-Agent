#!/bin/bash
# Phase 4 PoC Experiment for h-e1
# Error-Type Gating Improves Sample Efficiency

set -e

CODE_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_DIR="$CODE_DIR/outputs"
LOG="$OUTPUT_DIR/experiment.log"

mkdir -p "$OUTPUT_DIR"

# Completion marker finalizer - MUST be first after LOG
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

echo "Starting h-e1 PoC experiment at $(date -Iseconds)" | tee "$LOG"
echo "Output directory: $OUTPUT_DIR" | tee -a "$LOG"

# Run experiment with PoC-scale parameters
# 500 train samples, 500 test samples, 2000 steps (reduced for PoC)
python "$CODE_DIR/train.py" \
    --out_dir "$OUTPUT_DIR" \
    --total_steps 2000 \
    --eval_interval 200 \
    --train_size 500 \
    --test_size 500 \
    --seed 42 \
    2>&1 | tee -a "$LOG"

# Generate visualizations
echo "Generating figures..." | tee -a "$LOG"
python "$CODE_DIR/visualize.py" "$OUTPUT_DIR/experiment_results.json" "$CODE_DIR/../figures" 2>&1 | tee -a "$LOG"

echo "Experiment finished at $(date -Iseconds)" | tee -a "$LOG"
