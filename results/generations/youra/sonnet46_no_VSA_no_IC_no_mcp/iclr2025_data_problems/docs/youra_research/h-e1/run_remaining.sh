#!/usr/bin/env bash
# Run remaining 5 model evaluations in parallel across GPUs 1-4
set -uo pipefail

BASE=/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_data_problems/docs/youra_research/h-e1
RESULTS=$BASE/results
LOG_DIR=$BASE/logs_parallel

mkdir -p "$LOG_DIR"

source /home/PrayPrey/miniforge3/etc/profile.d/conda.sh
conda activate youra-h-e1

run_eval() {
    local model_id=$1
    local revision=$2
    local gpu=$3
    local log=$4

    mkdir -p "$(dirname "$log")"
    local slug
    slug=$(echo "$model_id" | tr '/' '-')
    local output_dir="$RESULTS/$slug-$revision"

    echo "[START] $model_id $revision on GPU $gpu" | tee "$log"

    for task in mmlu hellaswag arc_challenge winogrande; do
        task_out="$output_dir/$task"
        # Check if already done
        count=$(find "$task_out" -name "results_*.json" 2>/dev/null | wc -l)
        if [ "$count" -ge 1 ]; then
            echo "[SKIP] $task — already done" >> "$log"
            continue
        fi

        case $task in
            mmlu)         fewshot=5 ;;
            hellaswag)    fewshot=0 ;;
            arc_challenge) fewshot=25 ;;
            winogrande)   fewshot=5 ;;
        esac

        echo "[RUN] $task (${fewshot}-shot)" >> "$log"
        CUDA_VISIBLE_DEVICES=$gpu lm_eval \
            --model hf \
            --model_args "pretrained=$model_id,revision=$revision,dtype=float16,trust_remote_code=True" \
            --tasks "$task" \
            --num_fewshot "$fewshot" \
            --batch_size auto:4 \
            --output_path "$task_out" \
            --log_samples >> "$log" 2>&1
        status=$?
        if [ $status -ne 0 ]; then
            echo "[FAIL] $task exit=$status" >> "$log"
            # Try batch_size=1 on OOM
            echo "[RETRY] $task with batch_size=1" >> "$log"
            CUDA_VISIBLE_DEVICES=$gpu lm_eval \
                --model hf \
                --model_args "pretrained=$model_id,revision=$revision,dtype=float16,trust_remote_code=True" \
                --tasks "$task" \
                --num_fewshot "$fewshot" \
                --batch_size 1 \
                --output_path "$task_out" \
                --log_samples >> "$log" 2>&1 || echo "[FAIL2] $task failed again" >> "$log"
        else
            echo "[OK] $task" >> "$log"
        fi
    done
    echo "[DONE] $model_id $revision" >> "$log"
}

# Run in parallel: group by GPU
# GPU1: 160m-deduped + 410m-deduped  (small, can sequence)
# GPU2: 1b-deduped
# GPU3: 6.9b pile
# GPU4: 6.9b-deduped

run_eval "EleutherAI/pythia-160m-deduped"  "step143000" 1 "$LOG_DIR/160m_dedup.log" &
PID1=$!

run_eval "EleutherAI/pythia-410m-deduped"  "step143000" 2 "$LOG_DIR/410m_dedup.log" &
PID2=$!

run_eval "EleutherAI/pythia-1b-deduped"    "step143000" 3 "$LOG_DIR/1b_dedup.log" &
PID3=$!

run_eval "EleutherAI/pythia-6.9b"          "step99000"  4 "$LOG_DIR/6.9b_pile.log" &
PID4=$!

echo "Launched 4 parallel jobs: PIDs $PID1 $PID2 $PID3 $PID4"
echo "Waiting for all to complete..."

wait $PID1; echo "160m-dedup done (exit=$?)"
wait $PID2; echo "410m-dedup done (exit=$?)"
wait $PID3; echo "1b-dedup done (exit=$?)"
wait $PID4; echo "6.9b-pile done (exit=$?)"

echo "Parallel phase complete. Starting 6.9b-deduped..."
run_eval "EleutherAI/pythia-6.9b-deduped"  "step143000" 4 "$LOG_DIR/6.9b_dedup.log"

echo "ALL DONE"
echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))"
