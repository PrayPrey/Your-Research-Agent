#!/bin/bash
# Parallel lm-eval runner — uses multiple GPUs simultaneously
# Each GPU handles one model at a time

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG="$SCRIPT_DIR/../experiment.log"
RESULTS_DIR="$SCRIPT_DIR/results"
PAIRS_FILE="$SCRIPT_DIR/model_pairs.json"

trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

source /home/PrayPrey/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-e1

mkdir -p "$RESULTS_DIR"

echo "=== H-E1 Parallel Evaluation Start: $(date -Iseconds) ===" | tee -a "$LOG"

# Extract model IDs from pairs file
SFT_MODELS=$(python3 -c "
import json
with open('$PAIRS_FILE') as f: pairs = json.load(f)
for p in pairs: print(p['sft_model_id'])
")

DPO_MODELS=$(python3 -c "
import json
with open('$PAIRS_FILE') as f: pairs = json.load(f)
for p in pairs: print(p['dpo_model_id'])
")

ALL_MODELS=()
while IFS= read -r m; do ALL_MODELS+=("$m"); done <<< "$SFT_MODELS"
while IFS= read -r m; do ALL_MODELS+=("$m"); done <<< "$DPO_MODELS"

echo "Total models to evaluate: ${#ALL_MODELS[@]}" | tee -a "$LOG"

TASKS="truthfulqa_mc2,winogrande,winograd_wsc"
# bbq excluded initially — large dataset; include if time allows

eval_model() {
    local model_id="$1"
    local gpu_id="$2"
    local safe_id="${model_id//\//-}"  # replace / with -
    safe_id="${safe_id//--/--}"  # normalize
    local out_dir="$RESULTS_DIR/$safe_id"

    if [ -f "$out_dir/results.json" ]; then
        echo "[GPU$gpu_id] SKIP (cached): $model_id" | tee -a "$LOG"
        return 0
    fi

    echo "[GPU$gpu_id] START: $model_id" | tee -a "$LOG"
    CUDA_VISIBLE_DEVICES="$gpu_id" python -m lm_eval \
        --model hf \
        --model_args "pretrained=$model_id,dtype=bfloat16" \
        --tasks "$TASKS" \
        --batch_size 8 \
        --output_path "$out_dir" \
        2>&1 | tee -a "${LOG}.gpu${gpu_id}"

    local exit_code=$?
    if [ $exit_code -eq 0 ]; then
        echo "[GPU$gpu_id] DONE: $model_id" | tee -a "$LOG"
    else
        echo "[GPU$gpu_id] FAILED (exit=$exit_code): $model_id" | tee -a "$LOG"
    fi
}

export -f eval_model
export LOG RESULTS_DIR TASKS

# Run models in parallel across 5 GPUs
# Use GNU parallel or manual job management
GPU_COUNT=5
job_count=0
pids=()
gpu_assignments=()

for model_id in "${ALL_MODELS[@]}"; do
    gpu_id=$((job_count % GPU_COUNT))
    eval_model "$model_id" "$gpu_id" &
    pids+=($!)
    gpu_assignments+=($gpu_id)
    job_count=$((job_count + 1))

    # Limit concurrency to GPU_COUNT to avoid OOM
    if [ ${#pids[@]} -ge $GPU_COUNT ]; then
        wait "${pids[0]}"
        pids=("${pids[@]:1}")
        gpu_assignments=("${gpu_assignments[@]:1}")
    fi
done

# Wait for remaining jobs
for pid in "${pids[@]}"; do
    wait "$pid"
done

echo "=== All evaluations complete: $(date -Iseconds) ===" | tee -a "$LOG"
echo "=== Running classification pipeline ===" | tee -a "$LOG"

cd "$SCRIPT_DIR"
python3 -c "
import sys, os
sys.path.insert(0, '.')
import json, numpy as np

# Build matrix from whatever results are available
from build_score_matrix import build_matrix
from classify import main as classify_main
from visualize import main as viz_main
from report import main as report_main

RESULTS_DIR = 'results'
PAIRS_FILE = 'model_pairs.json'
FIGURES_DIR = '../figures'
os.makedirs(FIGURES_DIR, exist_ok=True)

X, y, model_ids = build_matrix(pairs_path=PAIRS_FILE, results_dir=RESULTS_DIR)
results = classify_main(X, y)
viz_main(X, y, results, model_ids, out_dir=FIGURES_DIR)
outcome = report_main(results)

# Save experiment_results.json
exp = {**results, 'outcome': outcome, 'model_ids': model_ids,
       'X': X.tolist(), 'y': y.tolist()}
with open('../experiment_results.json', 'w') as f:
    json.dump(exp, f, indent=2)
print(f'Experiment results saved. Outcome: {outcome}')
sys.exit(0 if outcome == 'PASS' else 1)
" 2>&1 | tee -a "$LOG"

echo "Pipeline complete." | tee -a "$LOG"
