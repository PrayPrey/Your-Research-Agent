#!/bin/bash
cd "$(dirname "$0")"
LOG=experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

export CUDA_VISIBLE_DEVICES=0,1,2,3,4
export HF_HOME=/home/PrayPrey/.cache/huggingface
export TRANSFORMERS_CACHE=/home/PrayPrey/.cache/huggingface/transformers

python train.py 2>&1 | tee "$LOG"
