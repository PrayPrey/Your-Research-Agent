#!/bin/bash
LOG="/home/anonymous/YouRA_results_new_4/TEST_scope_4/docs/youra_research/20260508_scope/h-m3/experiment.log"
CODE_DIR="/home/anonymous/YouRA_results_new_4/TEST_scope_4/docs/youra_research/20260508_scope/h-m3/code"
PYTHON="/home/anonymous/miniforge3/envs/youra-h-m3/bin/python"

trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

cd "$CODE_DIR"
"$PYTHON" run_experiment.py --config config.yaml >> "$LOG" 2>&1
