#!/bin/bash
# Smart parallel eval: 5 GPUs x 3 models = 15 workers
# Each GPU handles ~31 checkpoints per model in parallel
# GPUs 0,1 -> 70m; GPUs 1,2 -> 1b; GPUs 2,3,4 -> 6.9b (needs more GPU memory)

set -e
cd /home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_data_problems

CONDA_PATH=/home/PrayPrey/miniforge3
source $CONDA_PATH/etc/profile.d/conda.sh

LOG_DIR=results/h-m2/logs
mkdir -p $LOG_DIR

LOG=results/h-m2/eval_parallel2.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

echo "Starting optimized parallel evaluation $(date)" | tee $LOG

# Function: evaluate a chunk of steps for one model on one GPU
eval_chunk() {
    local MODEL_SIZE=$1
    local GPU_ID=$2
    local STEPS_STR=$3  # space-separated step list

    CUDA_VISIBLE_DEVICES=$GPU_ID conda run -n youra-h-m2 python -c "
import sys, os
sys.path.insert(0, 'docs/youra_research/h-m2/code')
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
import config
from src.evaluator import evaluate_checkpoint
import logging
logging.basicConfig(level=logging.WARNING)
steps = [int(s) for s in '$STEPS_STR'.split()]
for step in steps:
    try:
        scores = evaluate_checkpoint('$MODEL_SIZE', step, device='cuda')
        print(f'$MODEL_SIZE step {step}: {scores}', flush=True)
    except Exception as e:
        print(f'$MODEL_SIZE step {step} FAILED: {e}', flush=True)
" >> $LOG_DIR/eval_${MODEL_SIZE}_gpu${GPU_ID}.log 2>&1 &
}

# Split 154 steps across GPUs
# Steps 0-512 (11 early) + 1000-143000 (143 thousand-steps)
# 70m: GPU 0 (steps 0..60k) + GPU 1 (steps 61k..143k + early)
# 1b: GPU 2 (all steps)
# 6.9b: GPU 3 (steps 0..70k) + GPU 4 (steps 71k..143k + early)

EARLY="0 1 2 4 8 16 32 64 128 256 512"
STEPS_A="" # 1000-70000
STEPS_B="" # 71000-143000
for s in $(seq 1000 1000 70000); do STEPS_A="$STEPS_A $s"; done
for s in $(seq 71000 1000 143000); do STEPS_B="$STEPS_B $s"; done

# 70m: 2 GPUs
eval_chunk 70m 0 "$EARLY $STEPS_A"
eval_chunk 70m 1 "$STEPS_B"

# 1b: 1 GPU (use auto batch size)
eval_chunk 1b 2 "$EARLY $STEPS_A $STEPS_B"

# 6.9b: 2 GPUs
eval_chunk 6.9b 3 "$EARLY $STEPS_A"
eval_chunk 6.9b 4 "$STEPS_B"

echo "All workers launched. Waiting..." | tee -a $LOG

# Wait for all background jobs
wait

echo "All evaluations complete $(date)" | tee -a $LOG
