#!/bin/bash
# H-M2 Experiment Launcher
# Uses youra-h-e1 env for inference (has torch+transformers)
# Then runs statistical analysis with statsmodels/matplotlib

LOG=/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_scope/docs/youra_research/h-m2/experiment.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

CONDA_PATH=/home/PrayPrey/miniforge3
ENV_NAME=youra-h-e1  # Has torch, transformers, datasets, statsmodels, matplotlib
CODE_DIR=$(cd "$(dirname "$0")" && pwd)

echo "=== H-M2 Experiment: $(date -Iseconds) ===" > "$LOG"
echo "Code dir: $CODE_DIR" >> "$LOG"

source "$CONDA_PATH/etc/profile.d/conda.sh"
conda activate "$ENV_NAME"

echo "Python: $(which python)" >> "$LOG"
echo "Conda env: $CONDA_DEFAULT_ENV" >> "$LOG"

# Ensure analysis deps available
pip install -q statsmodels matplotlib seaborn scipy 2>> "$LOG"

cd "$CODE_DIR"

# Step 1: Generate proxy H-E1 data (LLaMA inference)
echo "=== Step 1: Generate proxy H-E1 data ===" >> "$LOG"
python generate_proxy_h_e1.py >> "$LOG" 2>&1

# Step 2: Run statistical analysis
echo "=== Step 2: Statistical Analysis ===" >> "$LOG"
python run_analysis.py >> "$LOG" 2>&1

echo "=== H-M2 Done ===" >> "$LOG"
