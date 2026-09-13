#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

LOG=logs/experiment_run.log
mkdir -p logs

# Install completion marker finalizer FIRST
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

echo "=== h-e1 Semantic Entropy Baseline Validation ===" | tee -a "$LOG"
echo "Start: $(date -Iseconds)" | tee -a "$LOG"

# Check for CUDA
if ! command -v nvidia-smi &> /dev/null; then
    echo "ERROR: nvidia-smi not found. GPU required." | tee -a "$LOG"
    exit 1
fi

echo "GPU Info:" | tee -a "$LOG"
nvidia-smi --query-gpu=name,memory.total --format=csv | tee -a "$LOG"

# Install dependencies (if not already installed)
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..." | tee -a "$LOG"
    python3 -m venv venv
    source venv/bin/activate
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    echo "Dependencies installed" | tee -a "$LOG"
else
    source venv/bin/activate
fi

# Check HuggingFace token
if [ -z "${HF_TOKEN:-}" ]; then
    echo "WARNING: HF_TOKEN not set. LLaMA-2 model may require authentication." | tee -a "$LOG"
    echo "Set via: export HF_TOKEN=your_token" | tee -a "$LOG"
fi

# Run experiment
echo "Starting experiment..." | tee -a "$LOG"
cd src
python main.py 2>&1 | tee -a "../$LOG"
EXIT_CODE=$?

cd ..
echo "Experiment finished with exit code: $EXIT_CODE" | tee -a "$LOG"
echo "End: $(date -Iseconds)" | tee -a "$LOG"

exit $EXIT_CODE
