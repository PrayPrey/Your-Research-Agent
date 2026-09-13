#!/usr/bin/env bash
# H-C1 Orchestration Script
# Sequential training → parallel eval (up to 4 GPUs) → analyze → figures
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

LOG="$SCRIPT_DIR/experiment.log"
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

echo "H-C1 Experiment Starting: $(date -Iseconds)" | tee "$LOG"
echo "Model: deepseek-ai/deepseek-coder-7b-base" | tee -a "$LOG"

CONDITIONS=(humaneval_only mbpp_only leetcode_only equal_mix)
SEEDS=(42 123 777)
_PY="/home/PrayPrey/miniforge3/envs/youra-h-c1/bin/python"
CHECKPOINT_DIR="$("$_PY" -c 'from config import CHECKPOINT_DIR; print(CHECKPOINT_DIR)')"
RESULTS_JSON="$("$_PY" -c 'from config import RESULTS_JSON; print(RESULTS_JSON)')"
FIGURES_DIR="$("$_PY" -c 'from config import FIGURES_DIR; print(FIGURES_DIR)')"

# ── STAGE 1: Training (sequential — one run per 4 GPUs) ─────────────────────────
CONDA_RUN="source /home/PrayPrey/miniforge3/etc/profile.d/conda.sh && conda run -n youra-h-c1"
TORCHRUN="/home/PrayPrey/miniforge3/envs/youra-h-c1/bin/torchrun"

echo "=== STAGE 1: Training ===" | tee -a "$LOG"
for condition in "${CONDITIONS[@]}"; do
  for seed in "${SEEDS[@]}"; do
    ckpt="$CHECKPOINT_DIR/condition_${condition}_seed_${seed}"
    if [ -d "$ckpt" ]; then
      echo "Skipping (exists): $ckpt" | tee -a "$LOG"
      continue
    fi
    echo "Training: condition=$condition seed=$seed" | tee -a "$LOG"
    "$TORCHRUN" --nproc_per_node=4 \
      --master_addr=localhost --master_port=29500 \
      train.py \
        --condition "$condition" \
        --seed "$seed" \
        2>&1 | tee -a "$LOG"
  done
done
echo "Training complete." | tee -a "$LOG"

# ── STAGE 2: Evaluation (parallel across 4 GPUs) ────────────────────────────────
echo "=== STAGE 2: Evaluation ===" | tee -a "$LOG"
# Use sem (GNU parallel) for 4-parallel eval if available, else sequential
PYTHON="/home/PrayPrey/miniforge3/envs/youra-h-c1/bin/python"

if command -v sem &>/dev/null; then
  for condition in "${CONDITIONS[@]}"; do
    for seed in "${SEEDS[@]}"; do
      for bench in humaneval mbpp; do
        sem -j4 "$PYTHON" evaluate.py \
          --condition "$condition" \
          --seed "$seed" \
          --benchmark "$bench" \
          --checkpoint_dir "$CHECKPOINT_DIR" \
          2>&1 | tee -a "$LOG"
      done
    done
  done
  sem --wait
else
  echo "[WARN] sem not found; running eval sequentially" | tee -a "$LOG"
  "$PYTHON" evaluate.py --all 2>&1 | tee -a "$LOG"
fi
echo "Evaluation complete." | tee -a "$LOG"

# ── STAGE 3: Analysis ────────────────────────────────────────────────────────────
echo "=== STAGE 3: Analysis ===" | tee -a "$LOG"
"$PYTHON" analyze.py \
  --results_json "$RESULTS_JSON" \
  2>&1 | tee -a "$LOG"
echo "Analysis complete." | tee -a "$LOG"

# ── STAGE 4: Figures ─────────────────────────────────────────────────────────────
echo "=== STAGE 4: Figures ===" | tee -a "$LOG"
"$PYTHON" figures.py \
  --results_json "$RESULTS_JSON" \
  --figures_dir "$FIGURES_DIR" \
  2>&1 | tee -a "$LOG"
echo "Figures complete." | tee -a "$LOG"

echo "H-C1 Experiment DONE: $(date -Iseconds)" | tee -a "$LOG"
