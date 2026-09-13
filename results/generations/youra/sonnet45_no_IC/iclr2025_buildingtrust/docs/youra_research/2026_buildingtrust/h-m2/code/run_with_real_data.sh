#!/bin/bash
set -e

LOG=/workspace/TEST_buildingtrust/docs/youra_research/h-m1/code/experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

echo "Starting H-M1 experiment with real TruthfulQA dataset..." | tee -a "$LOG"
echo "Timestamp: $(date -Iseconds)" | tee -a "$LOG"

source /home/anonymous/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-m1

cd /workspace/TEST_buildingtrust/docs/youra_research/h-m1/code

# Set model size (7B for faster execution)
export MODEL_SIZE=7b

# Run experiment
python run_experiment.py >> "$LOG" 2>&1

echo "Experiment finished at $(date -Iseconds)" | tee -a "$LOG"
