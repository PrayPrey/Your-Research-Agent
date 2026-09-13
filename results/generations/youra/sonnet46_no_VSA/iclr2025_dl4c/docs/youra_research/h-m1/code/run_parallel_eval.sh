#!/bin/bash
# Parallel fast_eval across 5 GPUs. Each GPU handles ~5 evals sequentially.
source /home/PrayPrey/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-e2

CKPT_BASE=/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_dl4c/docs/youra_research/h-e2/checkpoints
CODE_DIR=/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_dl4c/docs/youra_research/h-e2/code
RESULTS_BASE=/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_dl4c/docs/youra_research/h-e2/results
FAST_RESULTS=$RESULTS_BASE/fast_eval
CSV=$RESULTS_BASE/all_results.csv

mkdir -p "$FAST_RESULTS"
cd "$CODE_DIR"

# All 24 combos: condition seed benchmark
ALL_COMBOS=(
  "humaneval_only 42 humaneval"
  "humaneval_only 42 mbpp"
  "humaneval_only 123 humaneval"
  "humaneval_only 123 mbpp"
  "humaneval_only 777 humaneval"
  "humaneval_only 777 mbpp"
  "mbpp_only 42 humaneval"
  "mbpp_only 42 mbpp"
  "mbpp_only 123 humaneval"
  "mbpp_only 123 mbpp"
  "mbpp_only 777 humaneval"
  "mbpp_only 777 mbpp"
  "leetcode_only 42 humaneval"
  "leetcode_only 42 mbpp"
  "leetcode_only 123 humaneval"
  "leetcode_only 123 mbpp"
  "leetcode_only 777 humaneval"
  "leetcode_only 777 mbpp"
  "equal_mix 42 humaneval"
  "equal_mix 42 mbpp"
  "equal_mix 123 humaneval"
  "equal_mix 123 mbpp"
  "equal_mix 777 humaneval"
  "equal_mix 777 mbpp"
)

run_on_gpu() {
  local GPU=$1
  shift
  local COMBOS=("$@")
  for COMBO in "${COMBOS[@]}"; do
    read -r COND SEED BENCH <<< "$COMBO"
    echo "[GPU$GPU] $COND seed=$SEED $BENCH"
    CUDA_VISIBLE_DEVICES=$GPU python fast_eval.py \
      --condition "$COND" \
      --seed "$SEED" \
      --benchmark "$BENCH" \
      --checkpoint_dir "$CKPT_BASE/condition_${COND}_seed_${SEED}" \
      --results_csv "$CSV" \
      --output_dir "$FAST_RESULTS" \
      --device "cuda:0"
  done
}

# Split 24 across 5 GPUs: GPU0=5, GPU1=5, GPU2=5, GPU3=5, GPU4=4
run_on_gpu 0 "${ALL_COMBOS[@]:0:5}" &
run_on_gpu 1 "${ALL_COMBOS[@]:5:5}" &
run_on_gpu 2 "${ALL_COMBOS[@]:10:5}" &
run_on_gpu 3 "${ALL_COMBOS[@]:15:5}" &
run_on_gpu 4 "${ALL_COMBOS[@]:20:4}" &

wait
echo "ALL PARALLEL EVAL DONE"
