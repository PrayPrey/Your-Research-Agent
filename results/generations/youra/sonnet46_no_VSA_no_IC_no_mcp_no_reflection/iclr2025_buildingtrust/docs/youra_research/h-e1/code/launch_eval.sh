#!/bin/bash
# Launch parallel lm-eval across 5 H100 GPUs
# Each model runs on a dedicated GPU

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG="$SCRIPT_DIR/../experiment.log"
RESULTS_DIR="$SCRIPT_DIR/results"
PYTHON="/home/PrayPrey/miniforge3/envs/youra-h-e1-v2/bin/python"

trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

mkdir -p "$RESULTS_DIR"
cd "$SCRIPT_DIR"

echo "=== H-E1 Launch: $(date -Iseconds) ===" | tee "$LOG"
echo "GPU count: $(nvidia-smi -L | wc -l)" | tee -a "$LOG"

TASKS="truthfulqa_mc2,bbq,winogrande,winogender_all"

# All 12 models (6 pairs × 2)
MODELS=(
    "mistralai/Mistral-7B-Instruct-v0.1"
    "HuggingFaceH4/zephyr-7b-alpha"
    "teknium/OpenHermes-2.5-Mistral-7B"
    "HuggingFaceH4/zephyr-7b-beta"
    "allenai/tulu-2-7b"
    "allenai/tulu-2-dpo-7b"
    "meta-llama/Llama-2-7b-chat-hf"
    "Intel/neural-chat-7b-v3-1"
    "openchat/openchat_3.5"
    "berkeley-nest/Starling-LM-7B-alpha"
    "mistralai/Mistral-7B-Instruct-v0.3"
    "Intel/neural-chat-7b-v3-3"
)

eval_model() {
    local model_id="$1"
    local gpu_id="$2"
    local safe_id="${model_id//\//-}"
    # Remove double-dashes from safe path
    local out_dir="$RESULTS_DIR/$safe_id"
    local model_log="$out_dir/eval.log"

    if ls "$out_dir"/*.json "$out_dir"/results.json 2>/dev/null | head -1 | grep -q .; then
        echo "[GPU$gpu_id] SKIP (cached): $model_id" | tee -a "$LOG"
        return 0
    fi
    if find "$out_dir" -name "results.json" 2>/dev/null | grep -q .; then
        echo "[GPU$gpu_id] SKIP (cached): $model_id" | tee -a "$LOG"
        return 0
    fi

    mkdir -p "$out_dir"
    echo "[GPU$gpu_id] START: $model_id $(date -Iseconds)" | tee -a "$LOG"

    CUDA_VISIBLE_DEVICES="$gpu_id" "$PYTHON" -m lm_eval \
        --model hf \
        --model_args "pretrained=$model_id,dtype=bfloat16" \
        --tasks "$TASKS" \
        --batch_size 8 \
        --output_path "$out_dir" \
        > "$model_log" 2>&1

    local exit_code=$?
    if [ $exit_code -eq 0 ]; then
        echo "[GPU$gpu_id] DONE: $model_id $(date -Iseconds)" | tee -a "$LOG"
    else
        echo "[GPU$gpu_id] FAILED (exit=$exit_code): $model_id" | tee -a "$LOG"
        tail -5 "$model_log" | tee -a "$LOG"
    fi
    return $exit_code
}

export RESULTS_DIR LOG TASKS PYTHON
export -f eval_model

# Run 5 at a time (one per GPU), then next batch
GPU_COUNT=5
TOTAL=${#MODELS[@]}
echo "Launching $TOTAL model evaluations across $GPU_COUNT GPUs..." | tee -a "$LOG"

pids=()
gpu_ids=()

for i in "${!MODELS[@]}"; do
    model="${MODELS[$i]}"
    gpu_id=$((i % GPU_COUNT))

    eval_model "$model" "$gpu_id" &
    pids+=($!)
    gpu_ids+=($gpu_id)

    # When we have GPU_COUNT jobs running, wait for one to finish before launching more
    if [ ${#pids[@]} -ge $GPU_COUNT ]; then
        wait "${pids[0]}"
        pids=("${pids[@]:1}")
        gpu_ids=("${gpu_ids[@]:1}")
    fi
done

# Wait for all remaining
for pid in "${pids[@]}"; do
    wait "$pid" || true
done

echo "=== All model evaluations done: $(date -Iseconds) ===" | tee -a "$LOG"

# Run classification + reporting
echo "Running classification pipeline..." | tee -a "$LOG"
"$PYTHON" -c "
import sys, os, json
sys.path.insert(0, '.')

from build_score_matrix import build_matrix
from classify import main as classify_main
from visualize import main as viz_main
from report import main as report_main

RESULTS_DIR = 'results'
PAIRS_FILE = 'model_pairs.json'
FIGURES_DIR = '../figures'
os.makedirs(FIGURES_DIR, exist_ok=True)

print('Building score matrix...')
X, y, model_ids = build_matrix(pairs_path=PAIRS_FILE, results_dir=RESULTS_DIR)
print('Running classification...')
results = classify_main(X, y)
print('Generating figures...')
viz_main(X, y, results, model_ids, out_dir=FIGURES_DIR)
print('Generating report...')
outcome = report_main(results)

exp = {**results, 'outcome': outcome, 'model_ids': model_ids,
       'X': X.tolist(), 'y': y.tolist()}
with open('../experiment_results.json', 'w') as f:
    json.dump(exp, f, indent=2)
print(f'experiment_results.json saved. Outcome: {outcome}')
sys.exit(0 if outcome == 'PASS' else 1)
" 2>&1 | tee -a "$LOG"
