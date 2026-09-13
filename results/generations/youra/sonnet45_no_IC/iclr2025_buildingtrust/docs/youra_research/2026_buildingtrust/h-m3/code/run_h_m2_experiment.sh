#!/usr/bin/env bash
#
# H-M2 Experiment Launcher
# Runs fairness-reliability correlation analysis with proper error handling
#

set -euo pipefail

# Experiment configuration
LOG="experiment.log"
CONDA_PATH="/home/anonymous/miniforge3"
CONDA_ENV="youra-h-m2"
EXPERIMENT_SCRIPT="run_experiment_h_m2.py"

# MANDATORY: Install completion-marker finalizer (prevents unbounded waits)
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

echo "=== H-M2 Experiment Launcher ==="
echo "Started: $(date -Iseconds)"
echo "Conda env: $CONDA_ENV"
echo "Log file: $LOG"
echo ""

# Initialize conda
source "$CONDA_PATH/etc/profile.d/conda.sh"
conda activate "$CONDA_ENV"

# Verify conda environment
if [ "$CONDA_DEFAULT_ENV" != "$CONDA_ENV" ]; then
    echo "ERROR: Failed to activate conda environment $CONDA_ENV"
    exit 1
fi

echo "✓ Conda environment activated: $CONDA_DEFAULT_ENV"
echo ""

# Install required packages (idempotent)
echo "📦 Installing required packages..."
pip install -q torch transformers datasets scipy numpy matplotlib seaborn sentence-transformers scikit-learn openai pandas

echo "✓ Packages installed"
echo ""

# Set environment variables
export MODEL_SIZE="${MODEL_SIZE:-7b}"
export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:512"

echo "Configuration:"
echo "  MODEL_SIZE: $MODEL_SIZE"
echo "  Device: $(python -c 'import torch; print("CUDA" if torch.cuda.is_available() else "CPU")')"
echo ""

# Run experiment
echo "🚀 Running H-M2 experiment..."
echo "========================================"
python "$EXPERIMENT_SCRIPT" 2>&1 | tee -a "$LOG"
EXIT_CODE=${PIPESTATUS[0]}
echo "========================================"
echo ""

echo "Experiment finished: $(date -Iseconds)"
echo "Exit code: $EXIT_CODE"

# Output log summary
if [ -f "$LOG" ]; then
    echo ""
    echo "=== Log Summary ==="
    tail -20 "$LOG"
fi

exit $EXIT_CODE
