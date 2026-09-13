#!/bin/bash
# Parallel evaluation across model sizes using separate GPUs
# Runs all 154 checkpoints per model in background, one GPU each

set -e
CONDA_PATH=/home/PrayPrey/miniforge3
source $CONDA_PATH/etc/profile.d/conda.sh

cd /home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_data_problems

LOG_DIR=results/h-m2/logs
mkdir -p $LOG_DIR

echo "Starting parallel evaluation across 3 model sizes..."

# 70m on GPU 0
CUDA_VISIBLE_DEVICES=0 conda run -n youra-h-m2 python docs/youra_research/h-m2/code/run_experiment.py \
    --model-sizes 70m --device cuda 2>&1 > $LOG_DIR/eval_70m.log &
PID_70M=$!

# 1b on GPU 1
CUDA_VISIBLE_DEVICES=1 conda run -n youra-h-m2 python docs/youra_research/h-m2/code/run_experiment.py \
    --model-sizes 1b --device cuda 2>&1 > $LOG_DIR/eval_1b.log &
PID_1B=$!

# 6.9b on GPU 2
CUDA_VISIBLE_DEVICES=2 conda run -n youra-h-m2 python docs/youra_research/h-m2/code/run_experiment.py \
    --model-sizes 6.9b --device cuda 2>&1 > $LOG_DIR/eval_6.9b.log &
PID_6B=$!

echo "PIDs: 70m=$PID_70M, 1b=$PID_1B, 6.9b=$PID_6B"
echo "Waiting for all evaluations..."

wait $PID_70M && echo "70m DONE" || echo "70m FAILED"
wait $PID_1B && echo "1b DONE" || echo "1b FAILED"
wait $PID_6B && echo "6.9b DONE" || echo "6.9b FAILED"

echo "All evaluations complete."
