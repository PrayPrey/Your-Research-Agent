#!/bin/bash
# H-M1 experiment launcher
set -e

export PROJECT_ROOT="/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_wsl"
export H_M1_CODE="$PROJECT_ROOT/docs/youra_research/h-m1/code"
export H_E1_CODE="$PROJECT_ROOT/docs/youra_research/h-e1/code"
export CNN_ZOO="/home/PrayPrey/BACKUP/YouRA_results_new_4_sonnet45/TEST_wsl_opus45_2/docs/youra_research/20260402_wsl/_archive/20260402T071455_routing_recovery/h-e1/data/cnn_zoo/cifar_small_seed/tune_zoo_cifar10_uniform_small"

LOG="$PROJECT_ROOT/docs/youra_research/h-m1/experiment.log"
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

source /home/PrayPrey/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-m-integrated

python "$PROJECT_ROOT/docs/youra_research/h-m1/run_h_m1.py" \
    --epochs 50 \
    --seeds 0 1 2 \
    --device cuda \
    "$@" 2>&1 | tee "$LOG"
