#!/bin/bash
# H-E1 Experiment Launcher with completion marker
# Runs SAM+SWA experiments following unattended mode guidelines

set -e  # Exit on error

LOG="experiment_full.log"

# MANDATORY: Install completion-marker finalizer (runs on success, failure, OOM, SIGTERM, Ctrl-C)
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

# Configure experiment parameters
METHODS=("ERM" "SAM" "SWA" "Joint" "Sequential")
DATASETS=("ColoredMNIST")  # Start with ColoredMNIST only due to time constraints
SEEDS=(42 123 456)  # Use 3 seeds for faster execution (can extend to 5 later)
OUTPUT_DIR="outputs/h-e1"

# Redirect all output to log
{
    echo "==========================="
    echo "H-E1 EXPERIMENT EXECUTION"
    echo "==========================="
    echo "Start time: $(date -Iseconds)"
    echo "Methods: ${METHODS[@]}"
    echo "Datasets: ${DATASETS[@]}"
    echo "Seeds: ${SEEDS[@]}"
    echo "Output: $OUTPUT_DIR"
    echo "==========================="
    echo ""

    # Create output directory
    mkdir -p "$OUTPUT_DIR"

    # Run experiments with Python
    cd /workspace/TEST_scsl/experiments/h-e1
    python3 run_experiments.py \
        --output-dir "$OUTPUT_DIR" \
        --methods "${METHODS[@]}" \
        --datasets "${DATASETS[@]}" \
        --seeds "${SEEDS[@]}"

    echo ""
    echo "==========================="
    echo "EXPERIMENTS COMPLETED"
    echo "End time: $(date -Iseconds)"
    echo "==========================="

} > "$LOG" 2>&1
