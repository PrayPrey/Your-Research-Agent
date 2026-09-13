#!/usr/bin/env bash
# H-E2 Orchestration Script
# Usage: bash run_all.sh [--smoke]
# Runs: prepare_data (4 conditions) → train (12 runs) → evaluate (24 runs) → analyze

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
CODE_DIR="$SCRIPT_DIR"
DATA_DIR="$SCRIPT_DIR/../data/sft_sources"
CHECKPOINT_DIR="$SCRIPT_DIR/../checkpoints"
RESULTS_DIR="$SCRIPT_DIR/../results"
FIGURES_DIR="$SCRIPT_DIR/../figures"
RESULTS_CSV="$RESULTS_DIR/all_results.csv"

SMOKE=false
if [[ "${1:-}" == "--smoke" ]]; then
  SMOKE=true
  echo "[SMOKE] Running in smoke-test mode (5 steps, tiny data)"
fi

CONDITIONS=(humaneval_only mbpp_only leetcode_only equal_mix)
SEEDS=(42 123 777)

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate youra-h-e2

cd "$SCRIPT_DIR"

# ─── Stage 1: Data preparation ───────────────────────────────────────────────
echo ""
echo "=============================="
echo "STAGE 1: Data Preparation"
echo "=============================="
SMOKE_FLAG=""
if $SMOKE; then SMOKE_FLAG="--smoke"; fi

python prepare_data.py \
    --condition all \
    --output_dir "$DATA_DIR" \
    $SMOKE_FLAG

echo "Stage 1 complete."

# ─── Stage 2: SFT Training (12 runs) ─────────────────────────────────────────
echo ""
echo "=============================="
echo "STAGE 2: SFT Training"
echo "=============================="

for CONDITION in "${CONDITIONS[@]}"; do
  for SEED in "${SEEDS[@]}"; do
    echo ""
    echo "--- Training: condition=$CONDITION seed=$SEED ---"
    CKPT_DIR="$CHECKPOINT_DIR/condition_${CONDITION}_seed_${SEED}"

    if [[ -d "$CKPT_DIR" ]]; then
      echo "Checkpoint exists, skipping: $CKPT_DIR"
      continue
    fi

    if $SMOKE; then
      python train.py \
          --condition "$CONDITION" \
          --seed "$SEED" \
          --data_dir "$DATA_DIR" \
          --output_dir "$CHECKPOINT_DIR" \
          --smoke \
          --skip_activation_check
    else
      accelerate launch \
          --config_file "$CODE_DIR/accelerate_config.yaml" \
          "$CODE_DIR/train.py" \
          --condition "$CONDITION" \
          --seed "$SEED" \
          --data_dir "$DATA_DIR" \
          --output_dir "$CHECKPOINT_DIR"
    fi

    echo "Training done: $CONDITION seed=$SEED"
  done
done

echo "Stage 2 complete."

# ─── Stage 3: Evaluation (24 runs: 12 checkpoints × 2 benchmarks) ─────────────
echo ""
echo "=============================="
echo "STAGE 3: EvalPlus Evaluation"
echo "=============================="

mkdir -p "$RESULTS_DIR"

if $SMOKE; then
  python evaluate.py --smoke \
      --condition humaneval_only --seed 42 --benchmark humaneval \
      --checkpoint_dir "$CHECKPOINT_DIR/condition_humaneval_only_seed_42" \
      --results_csv "$RESULTS_CSV" \
      --evalplus_output_dir "$RESULTS_DIR"
else
  for CONDITION in "${CONDITIONS[@]}"; do
    for SEED in "${SEEDS[@]}"; do
      CKPT_DIR="$CHECKPOINT_DIR/condition_${CONDITION}_seed_${SEED}"
      if [[ ! -d "$CKPT_DIR" ]]; then
        echo "[WARN] Checkpoint missing, skipping eval: $CKPT_DIR"
        continue
      fi
      for BENCHMARK in humaneval mbpp; do
        echo "--- Evaluating: $CONDITION seed=$SEED on $BENCHMARK ---"
        python evaluate.py \
            --condition "$CONDITION" \
            --seed "$SEED" \
            --benchmark "$BENCHMARK" \
            --checkpoint_dir "$CKPT_DIR" \
            --results_csv "$RESULTS_CSV" \
            --evalplus_output_dir "$RESULTS_DIR"
      done
    done
  done
fi

echo "Stage 3 complete."

# ─── Stage 4: Statistical Analysis ───────────────────────────────────────────
echo ""
echo "=============================="
echo "STAGE 4: Statistical Analysis"
echo "=============================="

SMOKE_ANALYSIS_FLAG=""
if $SMOKE; then SMOKE_ANALYSIS_FLAG="--smoke"; fi

python analyze.py \
    --results_csv "$RESULTS_CSV" \
    --results_dir "$RESULTS_DIR" \
    --report_out "$RESULTS_DIR/statistical_report.txt" \
    --figures_dir "$FIGURES_DIR" \
    $SMOKE_ANALYSIS_FLAG

echo "Stage 4 complete."

echo ""
echo "=============================="
echo "ALL STAGES COMPLETE"
echo "  Report:  $RESULTS_DIR/statistical_report.txt"
echo "  Figures: $FIGURES_DIR/"
echo "=============================="
