"""Benchmark evaluation via lm-evaluation-harness with caching."""
from __future__ import annotations
import json
import logging
import os
from pathlib import Path

log = logging.getLogger(__name__)

METRIC_MAP = {
    "mmlu": "acc,none",
    "hellaswag": "acc_norm,none",
    "arc_challenge": "acc_norm,none",
    "winogrande": "acc,none",
}


def _extract_score(results: dict, task: str, metric_key: str) -> float | None:
    """Extract score from lm-eval results dict."""
    task_results = results.get("results", {})
    # mmlu is aggregate of subtasks
    if task == "mmlu":
        mmlu_key = next((k for k in task_results if k.startswith("mmlu") and "_" not in k.replace("mmlu", "")), None)
        if mmlu_key is None:
            # average across all mmlu subtasks
            scores = [
                v.get(metric_key, v.get("acc,none"))
                for k, v in task_results.items()
                if k.startswith("mmlu_")
                and isinstance(v, dict)
                and (metric_key in v or "acc,none" in v)
            ]
            return float(sum(scores) / len(scores)) if scores else None
        return task_results[mmlu_key].get(metric_key)
    elif task in task_results:
        t = task_results[task]
        return t.get(metric_key, t.get("acc,none") or t.get("acc_norm,none"))
    return None


def evaluate_checkpoint(
    model_id: str,
    step: int,
    tasks: dict[str, dict],
    cache_dir: Path,
    device: str = "cuda",
    batch_size: str = "auto",
    dtype: str = "float",
) -> dict[str, float]:
    """
    Evaluate model at checkpoint step using lm-evaluation-harness.
    Returns {task_name: score}. Reads cache if exists.
    """
    import lm_eval

    cache_dir = Path(cache_dir)
    model_size = model_id.split("/")[-1].replace("pythia-", "").replace("-deduped", "-deduped")
    # Derive size key from model_id
    size_key = model_id.split("/")[-1].replace("EleutherAI/pythia-", "").replace("pythia-", "")
    step_file = cache_dir / size_key / f"step{step:07d}.json"
    step_file.parent.mkdir(parents=True, exist_ok=True)

    if step_file.exists():
        try:
            cached = json.loads(step_file.read_text())
            scores = cached.get("scores", {})
            if all(t in scores for t in tasks):
                log.debug(f"Cache hit: {size_key} step{step}")
                return scores
        except Exception:
            pass

    log.info(f"Evaluating {model_id} at step{step} for tasks={list(tasks.keys())}")

    task_names = []
    for t in tasks:
        if t == "mmlu":
            task_names.append("mmlu")
        elif t == "hellaswag":
            task_names.append("hellaswag")
        elif t == "arc_challenge":
            task_names.append("arc_challenge")
        elif t == "winogrande":
            task_names.append("winogrande")

    results = lm_eval.simple_evaluate(
        model="hf",
        model_args=f"pretrained={model_id},revision=step{step},dtype={dtype}",
        tasks=task_names,
        num_fewshot=None,
        fewshot_as_multiturn=False,
        batch_size=batch_size,
        device=device,
        verbosity="WARNING",
    )

    scores = {}
    for task_name, cfg in tasks.items():
        metric_key = cfg["metric"]
        score = _extract_score(results, task_name, metric_key)
        if score is not None:
            scores[task_name] = float(score)
        else:
            log.warning(f"Score missing for {task_name} at {model_id} step{step}")

    step_file.write_text(json.dumps({
        "step": step,
        "model_id": model_id,
        "scores": scores,
    }, indent=2))

    return scores


def run_eval_all(
    model_sizes: list[str],
    model_ids: dict[str, str],
    checkpoint_steps: list[int],
    tasks: dict[str, dict],
    eval_cache_dir: str | Path,
    device: str = "cuda",
    batch_size: str = "auto",
    dtype: str = "float",
    resume: bool = True,
) -> dict[str, dict[int, dict[str, float]]]:
    """Run evaluations for all model sizes and checkpoints with resume support."""
    eval_cache_dir = Path(eval_cache_dir)
    all_results: dict[str, dict[int, dict[str, float]]] = {}

    for size in model_sizes:
        model_id = model_ids.get(size)
        if model_id is None:
            log.warning(f"No model_id for {size}, skipping")
            continue
        all_results[size] = {}
        for step in checkpoint_steps:
            cache_path = eval_cache_dir / size / f"step{step:07d}.json"
            if resume and cache_path.exists():
                try:
                    cached = json.loads(cache_path.read_text())
                    scores = cached.get("scores", {})
                    if all(t in scores for t in tasks):
                        all_results[size][step] = scores
                        continue
                except Exception:
                    pass
            try:
                scores = evaluate_checkpoint(
                    model_id, step, tasks, eval_cache_dir, device, batch_size, dtype
                )
                all_results[size][step] = scores
            except Exception as e:
                log.error(f"Eval failed for {size} step{step}: {e}")

    return all_results
