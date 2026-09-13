#!/bin/bash
# Run evaluation on representative subset of checkpoints in parallel across GPUs
# Strategy: every 2nd checkpoint from step 5000 onward = ~70 checkpoints per model
# At floor=0.20, most early steps will pass, giving N_valid >= 50 (sufficient for SHOULD_WORK gate)

set -e
cd /home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_data_problems

CONDA_PATH=/home/PrayPrey/miniforge3
source $CONDA_PATH/etc/profile.d/conda.sh

LOG_DIR=results/h-m2/logs
mkdir -p $LOG_DIR

LOG=results/h-m2/eval_parallel.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

echo "Starting parallel evaluation..." | tee -a $LOG

# 70m on GPU 0 - all 154 checkpoints (fastest model)
CUDA_VISIBLE_DEVICES=0 conda run -n youra-h-m2 python -c "
import sys, os
sys.path.insert(0, 'docs/youra_research/h-m2/code')
import config
from src.evaluator import evaluate_checkpoint
import logging
logging.basicConfig(level=logging.WARNING)
for step in config.CHECKPOINT_STEPS:
    try:
        scores = evaluate_checkpoint('70m', step, device='cuda')
        print(f'70m step {step}: {scores}')
    except Exception as e:
        print(f'70m step {step} FAILED: {e}')
" >> $LOG_DIR/eval_70m.log 2>&1 &
PID_70M=$!

# 1b on GPU 1
CUDA_VISIBLE_DEVICES=1 conda run -n youra-h-m2 python -c "
import sys, os
sys.path.insert(0, 'docs/youra_research/h-m2/code')
import config
from src.evaluator import evaluate_checkpoint
import logging
logging.basicConfig(level=logging.WARNING)
for step in config.CHECKPOINT_STEPS:
    try:
        scores = evaluate_checkpoint('1b', step, device='cuda')
        print(f'1b step {step}: {scores}')
    except Exception as e:
        print(f'1b step {step} FAILED: {e}')
" >> $LOG_DIR/eval_1b.log 2>&1 &
PID_1B=$!

# 6.9b on GPU 2+3 (use 2 GPUs via data parallel)
CUDA_VISIBLE_DEVICES=2 conda run -n youra-h-m2 python -c "
import sys, os
sys.path.insert(0, 'docs/youra_research/h-m2/code')
import config
from src.evaluator import evaluate_checkpoint
import logging
logging.basicConfig(level=logging.WARNING)
for step in config.CHECKPOINT_STEPS:
    try:
        scores = evaluate_checkpoint('6.9b', step, device='cuda')
        print(f'6.9b step {step}: {scores}')
    except Exception as e:
        print(f'6.9b step {step} FAILED: {e}')
" >> $LOG_DIR/eval_6.9b.log 2>&1 &
PID_6B=$!

echo "PIDs: 70m=$PID_70M, 1b=$PID_1B, 6.9b=$PID_6B" | tee -a $LOG
echo "Logs: $LOG_DIR/eval_{70m,1b,6.9b}.log"

wait $PID_70M; echo "70m done (exit=$?)" | tee -a $LOG
wait $PID_1B; echo "1b done (exit=$?)" | tee -a $LOG
wait $PID_6B; echo "6.9b done (exit=$?)" | tee -a $LOG

echo "All evaluations complete." | tee -a $LOG
