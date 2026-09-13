"""Pythia checkpoint evaluator with cache and fallback support."""
from __future__ import annotations
import json
import logging
from pathlib import Path
import numpy as np
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
import config

logger = logging.getLogger(__name__)


def is_cache_valid(cache_path: Path, required_tasks: list[str]) -> bool:
    if not cache_path.exists():
        return False
    try:
        data = json.loads(cache_path.read_text())
        return all(t in data.get("scores", {}) for t in required_tasks)
    except (json.JSONDecodeError, KeyError):
        return False


def load_cached_scores(cache_path: Path) -> dict[str, float]:
    return json.loads(cache_path.read_text())["scores"]


def evaluate_checkpoint(
    model_size: str,
    step: int,
    tasks: list[str] = None,
    device: str = "cuda",
    cache_dir: str = config.EVAL_CACHE_DIR,
    batch_size: str = config.BATCH_SIZE,
    dtype: str = config.DTYPE,
) -> dict[str, float]:
    """Evaluate one Pythia checkpoint. Returns {"mmlu": float, "hellaswag": float}."""
    if tasks is None:
        tasks = list(config.TASKS.keys())

    cache_path = Path(cache_dir) / model_size / f"step{step:07d}.json"
    if is_cache_valid(cache_path, tasks):
        logger.info(f"[{model_size}] step {step}: cache hit")
        return load_cached_scores(cache_path)

    import lm_eval

    model_id = config.MODEL_IDS[model_size]
    model_args = f"pretrained={model_id},revision=step{step},dtype={dtype}"

    # lm_eval requires num_fewshot as int (applied uniformly) or None (task default)
    # Use task-specific num_fewshot via task_manager approach: pass None to use task defaults
    results = lm_eval.simple_evaluate(
        model="hf",
        model_args=model_args,
        tasks=tasks,
        num_fewshot=None,  # use each task's default fewshot setting
        batch_size=batch_size,
        device=device,
    )

    scores: dict[str, float] = {}
    for task in tasks:
        metric_key = config.TASKS[task]["metric"]
        scores[task] = results["results"][task][metric_key]

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps({"step": step, "model_size": model_size, "scores": scores}))
    logger.info(f"[{model_size}] step {step}: {scores}")
    return scores


def batch_evaluate_model(
    model_size: str,
    steps: list[int] = None,
    tasks: list[str] = None,
    device: str = "cuda",
) -> dict[int, dict[str, float]]:
    """Evaluate all checkpoints for one model size with resume support."""
    if steps is None:
        steps = config.CHECKPOINT_STEPS
    if tasks is None:
        tasks = list(config.TASKS.keys())

    all_scores: dict[int, dict[str, float]] = {}
    for step in steps:
        scores = evaluate_checkpoint(model_size, step, tasks=tasks, device=device)
        all_scores[step] = scores
        logger.info(f"[{model_size}] step {step}: mmlu={scores.get('mmlu', 'N/A'):.4f}, hellaswag={scores.get('hellaswag', 'N/A'):.4f}")
    return all_scores


def load_scores_array(model_size: str, steps: list[int] = None) -> dict[str, np.ndarray]:
    """Load all cached JSONs; return {"mmlu": (154,), "hellaswag": (154,)}."""
    if steps is None:
        steps = config.CHECKPOINT_STEPS
    cache_dir = Path(config.EVAL_CACHE_DIR) / model_size

    mmlu_scores = []
    hellaswag_scores = []
    for step in steps:
        path = cache_dir / f"step{step:07d}.json"
        if path.exists():
            data = json.loads(path.read_text())
            mmlu_scores.append(data["scores"].get("mmlu", np.nan))
            hellaswag_scores.append(data["scores"].get("hellaswag", np.nan))
        else:
            mmlu_scores.append(np.nan)
            hellaswag_scores.append(np.nan)

    return {
        "mmlu": np.array(mmlu_scores),
        "hellaswag": np.array(hellaswag_scores),
    }


def load_fallback_scores(
    model_size: str,
    pythia_repo_dir: Path,
    steps: list[int] = None,
) -> dict[int, dict[str, float]]:
    """Load pre-cached eval results from pythia repo evals/pythia-v1/."""
    if steps is None:
        steps = config.CHECKPOINT_STEPS
    base = pythia_repo_dir / "evals" / "pythia-v1" / f"pythia-{model_size}"
    if not base.exists():
        raise FileNotFoundError(f"Fallback dir not found: {base}")

    results: dict[int, dict[str, float]] = {}
    for step in steps:
        step_dir = base / f"step{step}"
        scores: dict[str, float] = {}
        for task in ["mmlu", "hellaswag"]:
            result_file = step_dir / f"results_{task}.json"
            if result_file.exists():
                data = json.loads(result_file.read_text())
                metric_key = config.TASKS[task]["metric"]
                scores[task] = data["results"][task][metric_key]
        if scores:
            results[step] = scores
    return results
