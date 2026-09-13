#!/usr/bin/env python3
"""
Run evaluations for H-M3: all 4 benchmarks for available model sizes.
Fills in missing arc_challenge + winogrande for cached steps,
then runs full 154-checkpoint eval for each model size.
"""
import json
import logging
import os
import sys
from pathlib import Path
import concurrent.futures

sys.path.insert(0, str(Path(__file__).parent))
import config as cfg

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
log = logging.getLogger(__name__)

EVAL_CACHE = Path(cfg.EVAL_CACHE_DIR)
MODEL_SIZES_TO_EVAL = ["70m", "1b", "6.9b"]  # sizes with H-E1 data
MAX_GPUS = 5


def get_available_steps(size: str) -> set[int]:
    """Steps that already have all 4 benchmarks cached."""
    size_dir = EVAL_CACHE / size
    if not size_dir.exists():
        return set()
    complete = set()
    for f in size_dir.glob("*.json"):
        try:
            d = json.loads(f.read_text())
            scores = d.get("scores", {})
            if all(t in scores for t in cfg.TASKS):
                step = d.get("step", int(f.stem.replace("step", "")))
                complete.add(step)
        except Exception:
            pass
    return complete


def get_partial_steps(size: str) -> dict[int, dict]:
    """Steps with partial scores (missing arc_challenge or winogrande)."""
    size_dir = EVAL_CACHE / size
    if not size_dir.exists():
        return {}
    partial = {}
    for f in size_dir.glob("*.json"):
        try:
            d = json.loads(f.read_text())
            scores = d.get("scores", {})
            missing = [t for t in cfg.TASKS if t not in scores]
            if missing:
                step = d.get("step", int(f.stem.replace("step", "")))
                partial[step] = {"existing_scores": scores, "missing": missing}
        except Exception:
            pass
    return partial


def eval_step(model_id: str, size: str, step: int, device: str, existing_scores: dict = None) -> dict:
    """Evaluate one checkpoint. Returns scores dict."""
    import lm_eval

    cache_file = EVAL_CACHE / size / f"step{step:07d}.json"
    cache_file.parent.mkdir(parents=True, exist_ok=True)

    # Determine which tasks to run
    existing = existing_scores or {}
    tasks_to_run = [t for t in cfg.TASKS if t not in existing]
    if not tasks_to_run:
        return existing

    # Build fewshot map
    num_fewshot = {
        "mmlu": 5,
        "hellaswag": 10,
        "arc_challenge": 25,
        "winogrande": 5,
    }

    log.info(f"Evaluating {size} step{step} tasks={tasks_to_run} on {device}")

    try:
        results = lm_eval.simple_evaluate(
            model="hf",
            model_args=f"pretrained={model_id},revision=step{step},dtype=float",
            tasks=tasks_to_run,
            num_fewshot=None,  # use task defaults
            batch_size="auto",
            device=device,
            verbosity="ERROR",
        )

        scores = dict(existing)
        task_results = results.get("results", {})

        for task in tasks_to_run:
            metric = cfg.TASKS[task]["metric"]
            if task == "mmlu":
                # average over subtasks
                subtask_scores = [
                    v.get(metric, v.get("acc,none"))
                    for k, v in task_results.items()
                    if k.startswith("mmlu_") and isinstance(v, dict)
                ]
                if not subtask_scores:
                    # try aggregate key
                    agg = task_results.get("mmlu", task_results.get("mmlu_abstract_algebra"))
                    if agg:
                        subtask_scores = [agg.get(metric, agg.get("acc,none"))]
                if subtask_scores:
                    scores[task] = float(sum(subtask_scores) / len(subtask_scores))
            elif task in task_results:
                t = task_results[task]
                s = t.get(metric, t.get("acc,none") or t.get("acc_norm,none"))
                if s is not None:
                    scores[task] = float(s)

        cache_file.write_text(json.dumps({"step": step, "model_size": size, "scores": scores}, indent=2))
        return scores

    except Exception as e:
        log.error(f"Eval failed for {size} step{step}: {e}")
        return existing


def run_size(size: str, gpu_id: int) -> None:
    """Run full eval for one model size on assigned GPU."""
    device = f"cuda:{gpu_id}"
    model_id = cfg.MODEL_IDS[size]
    log.info(f"Starting {size} on {device}")

    complete = get_available_steps(size)
    partial = get_partial_steps(size)
    all_steps = set(cfg.CHECKPOINT_STEPS)
    todo_steps = sorted(all_steps - complete)

    log.info(f"{size}: {len(complete)} complete, {len(partial)} partial, {len(todo_steps)} todo")

    for step in todo_steps:
        existing = partial.get(step, {}).get("existing_scores", {})
        eval_step(model_id, size, step, device, existing)

    complete_after = get_available_steps(size)
    log.info(f"{size}: DONE — {len(complete_after)}/154 checkpoints complete")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--sizes", nargs="+", default=MODEL_SIZES_TO_EVAL)
    parser.add_argument("--max-workers", type=int, default=3)
    args = parser.parse_args()

    sizes = args.sizes
    log.info(f"Running eval for sizes: {sizes}")

    # Assign GPUs round-robin
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.max_workers) as exe:
        futures = {
            exe.submit(run_size, size, i % MAX_GPUS): size
            for i, size in enumerate(sizes)
        }
        for future in concurrent.futures.as_completed(futures):
            size = futures[future]
            try:
                future.result()
                log.info(f"{size}: completed")
            except Exception as e:
                log.error(f"{size}: failed with {e}")

    print("EXPERIMENT COMPLETE (exit=0)")
