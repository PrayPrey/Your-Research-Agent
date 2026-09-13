#!/bin/bash
# Supplement H-M3 eval cache: add arc_challenge + winogrande for all steps
# Also copies completed H-M2 steps (mmlu+hellaswag) to H-M3 cache as they complete
# Runs 70m on GPU:1, 1b on GPU:2, 6.9b on GPU:3 (leaving 0,4 for H-M2)

set -e
cd /home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_data_problems

CONDA_PATH=/home/PrayPrey/miniforge3
source $CONDA_PATH/etc/profile.d/conda.sh

LOG=results/h-m3/supplement_eval.log
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT
echo "H-M3 supplement eval started $(date)" | tee "$LOG"

mkdir -p results/h-m3/eval_cache/70m
mkdir -p results/h-m3/eval_cache/1b
mkdir -p results/h-m3/eval_cache/6.9b

# Step 1: Sync from H-M2 cache (copy completed steps with mmlu+hellaswag scores)
python3 -c "
import json
from pathlib import Path

h2 = Path('results/h-m2/eval_cache')
h3 = Path('results/h-m3/eval_cache')
h3.mkdir(parents=True, exist_ok=True)

synced = 0
for size in ['70m', '1b', '6.9b']:
    src = h2 / size
    dst = h3 / size
    dst.mkdir(exist_ok=True)
    if not src.exists():
        continue
    for f in src.glob('*.json'):
        d = json.loads(f.read_text())
        scores = d.get('scores', {})
        dst_f = dst / f.name
        if dst_f.exists():
            existing = json.loads(dst_f.read_text())
            ex_scores = existing.get('scores', {})
            # merge: prefer h-m3 existing, add h-m2 scores for missing tasks
            merged = dict(scores)
            merged.update(ex_scores)  # h-m3 scores take precedence
            if merged != ex_scores:
                existing['scores'] = merged
                dst_f.write_text(json.dumps(existing, indent=2))
                synced += 1
        else:
            step = d.get('step', int(f.stem.replace('step','')))
            dst_f.write_text(json.dumps({'step': step, 'model_size': size, 'scores': scores}, indent=2))
            synced += 1

print(f'Synced {synced} files from H-M2 cache')
" 2>&1 | tee -a "$LOG"

# Step 2: Run arc_challenge + winogrande for 70m (GPU:1) in background
eval_model() {
    local SIZE=$1
    local GPU=$2
    local MODEL_ID=$3

    CUDA_VISIBLE_DEVICES=$GPU TOKENIZERS_PARALLELISM=false conda run -n youra-h-m3 python3 -c "
import sys, json, logging
sys.path.insert(0, 'docs/youra_research/h-m3/code')
import config as cfg
from pathlib import Path
import lm_eval

logging.basicConfig(level=logging.WARNING)

size = '$SIZE'
model_id = '$MODEL_ID'
device = 'cuda:0'  # CUDA_VISIBLE_DEVICES remaps this
cache_dir = Path(cfg.EVAL_CACHE_DIR) / size
cache_dir.mkdir(parents=True, exist_ok=True)

TASKS_TO_RUN = ['arc_challenge', 'winogrande']
TASK_METRICS = {'arc_challenge': 'acc_norm,none', 'winogrande': 'acc,none'}

steps_done = 0
for step in cfg.CHECKPOINT_STEPS:
    f = cache_dir / f'step{step:07d}.json'
    existing_scores = {}
    if f.exists():
        try:
            d = json.loads(f.read_text())
            existing_scores = d.get('scores', {})
        except Exception:
            pass
    missing = [t for t in TASKS_TO_RUN if t not in existing_scores]
    if not missing:
        continue

    try:
        results = lm_eval.simple_evaluate(
            model='hf',
            model_args=f'pretrained={model_id},revision=step{step},dtype=float',
            tasks=missing,
            batch_size='auto',
            device=device,
            verbosity='ERROR',
        )
        task_res = results.get('results', {})
        for task in missing:
            metric = TASK_METRICS[task]
            if task in task_res:
                s = task_res[task].get(metric, task_res[task].get('acc,none') or task_res[task].get('acc_norm,none'))
                if s is not None:
                    existing_scores[task] = float(s)
        out = {'step': step, 'model_size': size, 'scores': existing_scores}
        f.write_text(json.dumps(out, indent=2))
        steps_done += 1
        print(f'{size} step{step}: done ({steps_done})', flush=True)
    except Exception as e:
        print(f'{size} step{step}: ERROR {e}', flush=True)

print(f'{size}: completed {steps_done} new evaluations')
" 2>&1 | tee -a "results/h-m3/eval_${SIZE}.log" &
}

eval_model "70m" 1 "EleutherAI/pythia-70m" &
PID_70M=$!
eval_model "1b" 2 "EleutherAI/pythia-1b" &
PID_1B=$!
eval_model "6.9b" 3 "EleutherAI/pythia-6.9b" &
PID_69B=$!

echo "Waiting for eval jobs (PIDs: $PID_70M $PID_1B $PID_69B)..." | tee -a "$LOG"
wait $PID_70M && echo "70m done" | tee -a "$LOG"
wait $PID_1B && echo "1b done" | tee -a "$LOG"
wait $PID_69B && echo "6.9b done" | tee -a "$LOG"

echo "All eval jobs complete $(date)" | tee -a "$LOG"
