#!/bin/bash

set -e

LOG_FILE="../../results/experiment.log"
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG_FILE"' EXIT

echo "Starting h-e1 compressibility experiment..." | tee "$LOG_FILE"
echo "Timestamp: $(date -Iseconds)" | tee -a "$LOG_FILE"

cd "$(dirname "$0")"

METHODS=("ERM" "SAM")
SEEDS=(42 43)
DEVICE="cuda"

echo "" | tee -a "$LOG_FILE"
echo "==============================================================" | tee -a "$LOG_FILE"
echo "PHASE 1: Training models (2 seeds per method for validation)" | tee -a "$LOG_FILE"
echo "==============================================================" | tee -a "$LOG_FILE"

for METHOD in "${METHODS[@]}"; do
    for SEED in "${SEEDS[@]}"; do
        echo "" | tee -a "$LOG_FILE"
        echo "[$(date -Iseconds)] Training ${METHOD} seed ${SEED}..." | tee -a "$LOG_FILE"
        timeout 900 python train.py \
            --method "$METHOD" \
            --seed "$SEED" \
            --checkpoint-dir "../../results/checkpoints/" \
            --log-dir "../../results/logs/" \
            --device "$DEVICE" 2>&1 | tee -a "$LOG_FILE" || {
                echo "ERROR: Training ${METHOD} seed ${SEED} failed/timeout" | tee -a "$LOG_FILE"
            }
    done
done

echo "" | tee -a "$LOG_FILE"
echo "==============================================================" | tee -a "$LOG_FILE"
echo "PHASE 2: Pruning evaluation" | tee -a "$LOG_FILE"
echo "==============================================================" | tee -a "$LOG_FILE"

echo "[$(date -Iseconds)] Starting pruning evaluation..." | tee -a "$LOG_FILE"
timeout 1800 python prune.py \
    --checkpoint-dir "../../results/checkpoints/" \
    --output "../../results/h_e1_pruning_logs.csv" \
    --device "$DEVICE" 2>&1 | tee -a "$LOG_FILE" || {
        echo "ERROR: Pruning failed/timeout" | tee -a "$LOG_FILE"
    }

echo "" | tee -a "$LOG_FILE"
echo "==============================================================" | tee -a "$LOG_FILE"
echo "PHASE 3: Statistical analysis and gate evaluation" | tee -a "$LOG_FILE"
echo "==============================================================" | tee -a "$LOG_FILE"

echo "[$(date -Iseconds)] Running analysis..." | tee -a "$LOG_FILE"
python analysis.py \
    --pruning-logs "../../results/h_e1_pruning_logs.csv" \
    --output-dir "../../results/figures/" \
    --format "pdf" 2>&1 | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
echo "==============================================================" | tee -a "$LOG_FILE"
echo "Experiment complete at $(date -Iseconds)" | tee -a "$LOG_FILE"
echo "==============================================================" | tee -a "$LOG_FILE"
