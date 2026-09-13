#!/bin/bash

set -e

LOG_FILE="run_all_experiment.log"
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG_FILE"' EXIT

echo "Starting h-e1 compressibility experiment..." | tee "$LOG_FILE"
echo "Timestamp: $(date -Iseconds)" | tee -a "$LOG_FILE"

cd "$(dirname "$0")"

METHODS=("ERM" "SAM")
SEEDS=(42 43 44 45 46)
DEVICE="cuda"

echo "" | tee -a "$LOG_FILE"
echo "==============================================================" | tee -a "$LOG_FILE"
echo "PHASE 1: Training all models" | tee -a "$LOG_FILE"
echo "==============================================================" | tee -a "$LOG_FILE"

for METHOD in "${METHODS[@]}"; do
    for SEED in "${SEEDS[@]}"; do
        echo "" | tee -a "$LOG_FILE"
        echo "Training ${METHOD} with seed ${SEED}..." | tee -a "$LOG_FILE"
        timeout 900 python train.py \
            --method "$METHOD" \
            --seed "$SEED" \
            --checkpoint-dir "../../results/checkpoints/" \
            --log-dir "../../results/logs/" \
            --device "$DEVICE" 2>&1 | tee -a "$LOG_FILE" || {
                echo "ERROR: Training ${METHOD} seed ${SEED} failed or timed out" | tee -a "$LOG_FILE"
            }
    done
done

echo "" | tee -a "$LOG_FILE"
echo "==============================================================" | tee -a "$LOG_FILE"
echo "PHASE 2: Pruning and evaluation" | tee -a "$LOG_FILE"
echo "==============================================================" | tee -a "$LOG_FILE"

timeout 1800 python prune.py \
    --checkpoint-dir "../../results/checkpoints/" \
    --output "../../results/h_e1_pruning_logs.csv" \
    --device "$DEVICE" 2>&1 | tee -a "$LOG_FILE" || {
        echo "ERROR: Pruning phase failed or timed out" | tee -a "$LOG_FILE"
    }

echo "" | tee -a "$LOG_FILE"
echo "==============================================================" | tee -a "$LOG_FILE"
echo "PHASE 3: Statistical analysis" | tee -a "$LOG_FILE"
echo "==============================================================" | tee -a "$LOG_FILE"

python analysis.py \
    --pruning-logs "../../results/h_e1_pruning_logs.csv" \
    --output-dir "../../results/figures/" \
    --format "pdf" 2>&1 | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
echo "==============================================================" | tee -a "$LOG_FILE"
echo "Experiment complete!" | tee -a "$LOG_FILE"
echo "Results saved to ../../results/" | tee -a "$LOG_FILE"
echo "==============================================================" | tee -a "$LOG_FILE"
