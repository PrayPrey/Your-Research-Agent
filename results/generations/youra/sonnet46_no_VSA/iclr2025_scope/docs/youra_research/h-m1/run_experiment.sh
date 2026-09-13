#!/bin/bash
set -e

BASE=/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_scope/docs/youra_research/h-m1
CODE=$BASE/code
LOG=$BASE/experiment.log

trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

export HF_HUB_CACHE=/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_scope/docs/youra_research/h-e1/checkpoints/mohawk/huggingface/hub
export TRANSFORMERS_CACHE=$HF_HUB_CACHE
export CUDA_VISIBLE_DEVICES=0
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

PYTHON=/home/PrayPrey/miniforge3/envs/youra-h-e1-cx/bin/python

cd $CODE
echo "Starting h-m1 experiment at $(date)" | tee -a "$LOG"
$PYTHON run.py 2>&1 | tee -a "$LOG"
