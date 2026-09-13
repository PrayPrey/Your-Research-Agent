"""H-E1 Evaluation Pipeline: Run lm-eval-harness on Pythia checkpoints."""
import json
import os
import logging
from dataclasses import dataclass, asdict
from typing import Optional

import torch
from lm_eval import evaluator
from lm_eval.models.huggingface import HFLM

from config import CONFIG, PATHS, checkpoint_revision, model_id

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

@dataclass
class CheckpointResult:
    size: str
    step: int
    task: str
    score: float
    wikitext_ppl: float

def load_cache(cache_path: str) -> dict:
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as f:
            return json.load(f)
    return {}

def save_cache(cache_path: str, cache: dict) -> None:
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    with open(cache_path, 'w') as f:
        json.dump(cache, f, indent=2)

def evaluate_checkpoint(
    size: str,
    step: int,
    tasks: list[str],
    wikitext_task: str = "wikitext",
    seed: int = 1,
    batch_size: str = "auto",
) -> list[CheckpointResult]:
    """Evaluate single Pythia checkpoint on all tasks."""
    mid = model_id(CONFIG.hf_org, size)
    rev = checkpoint_revision(step)

    log.info(f"Evaluating {mid} @ {rev}")

    model = HFLM(
        pretrained=mid,
        revision=rev,
        batch_size=batch_size,
        device="cuda" if torch.cuda.is_available() else "cpu",
    )

    all_tasks = tasks + [wikitext_task]
    results = evaluator.simple_evaluate(
        model=model,
        tasks=all_tasks,
        batch_size=batch_size,
        random_seed=seed,
    )

    ppl = results["results"].get(wikitext_task, {}).get("word_perplexity,none",
           results["results"].get(wikitext_task, {}).get("word_perplexity", float('nan')))

    checkpoint_results = []
    for task in tasks:
        task_result = results["results"].get(task, {})
        score = task_result.get("acc,none", task_result.get("acc", 0.0))
        if isinstance(score, str):
            score = float(score)
        checkpoint_results.append(CheckpointResult(
            size=size,
            step=step,
            task=task,
            score=score,
            wikitext_ppl=ppl,
        ))

    return checkpoint_results

def run_all_evaluations(
    model_sizes: Optional[list[str]] = None,
    steps: Optional[list[int]] = None,
    tasks: Optional[list[str]] = None,
    wikitext_task: Optional[str] = None,
    cache_path: Optional[str] = None,
) -> list[CheckpointResult]:
    """Run evaluations across all checkpoints with caching."""
    model_sizes = model_sizes or CONFIG.model_sizes
    steps = steps or CONFIG.checkpoint_steps
    tasks = tasks or CONFIG.tasks
    wikitext_task = wikitext_task or CONFIG.wikitext_task
    cache_path = cache_path or PATHS.eval_cache_path

    cache = load_cache(cache_path)
    all_results = []

    for size in model_sizes:
        for step in steps:
            key = f"{size}_{step}"

            if key in cache:
                log.info(f"Cache hit: {key}")
                for item in cache[key]:
                    all_results.append(CheckpointResult(**item))
                continue

            try:
                checkpoint_results = evaluate_checkpoint(
                    size=size,
                    step=step,
                    tasks=tasks,
                    wikitext_task=wikitext_task,
                    seed=CONFIG.seed,
                )
                all_results.extend(checkpoint_results)
                cache[key] = [asdict(r) for r in checkpoint_results]
                save_cache(cache_path, cache)
                log.info(f"Cached: {key}")

            except Exception as e:
                log.error(f"Eval failed {key}: {e}")
                continue

    return all_results

if __name__ == "__main__":
    results = run_all_evaluations()
    print(f"Evaluated {len(results)} checkpoint-task pairs")
