#!/bin/bash
# h-m2 PoC experiment launcher

set -e

LOG=experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

echo "Starting h-m2 PoC experiment: ResNet-50 vs ViT-B/16"
echo "Log: $LOG"

cd "$(dirname "$0")"

# Install dependencies
echo "Installing dependencies..."
pip install -q torch torchvision timm wilds scipy matplotlib 2>&1 | tee -a "$LOG"

# Run full experiment (ResNet-50 + ViT-B/16)
echo "Running experiment..."
python main.py full > "$LOG" 2>&1
