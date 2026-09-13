#!/bin/bash
# Run h-m1 experiment with REAL Waterbirds data (no mock data)
# This script fixes the mock data issue detected by external verification

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

LOG="$SCRIPT_DIR/experiment.log"
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

echo "=== H-M1 Experiment: Real Data Execution ===" | tee "$LOG"
echo "Date: $(date)" | tee -a "$LOG"
echo "Directory: $SCRIPT_DIR" | tee -a "$LOG"

# Select GPU with most free memory
if command -v nvidia-smi &> /dev/null; then
    GPU_ID=$(nvidia-smi --query-gpu=index,memory.free --format=csv,noheader,nounits | sort -k2 -nr | head -1 | awk '{print $1}')
    export CUDA_VISIBLE_DEVICES=$GPU_ID
    echo "Using GPU $GPU_ID" | tee -a "$LOG"
else
    export CUDA_VISIBLE_DEVICES=""
    echo "No GPU available, using CPU" | tee -a "$LOG"
fi

# Install dependencies
echo "Installing dependencies..." | tee -a "$LOG"
pip install -q torch torchvision pandas pillow pyyaml scipy matplotlib seaborn 2>&1 | tee -a "$LOG" || true

# Install hessian-eigenthings
echo "Installing hessian-eigenthings..." | tee -a "$LOG"
pip install -q git+https://github.com/noahgolmant/pytorch-hessian-eigenthings.git 2>&1 | tee -a "$LOG" || true

# Download Waterbirds dataset
echo "Checking for Waterbirds dataset..." | tee -a "$LOG"
python download_waterbirds.py 2>&1 | tee -a "$LOG"

# Run experiment with timeout (2 hours max)
echo "Running h-m1 experiment..." | tee -a "$LOG"
timeout 7200 python run_h_m1_experiment.py --config config.yaml 2>&1 | tee -a "$LOG"

echo "Experiment completed" | tee -a "$LOG"
