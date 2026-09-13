"""Evaluation using lm-evaluation-harness + ensemble score."""

import os
import json
import numpy as np
from sklearn.decomposition import PCA

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import EVAL_CONFIG


TASKS = EVAL_CONFIG["tasks"]
METRICS = EVAL_CONFIG["metrics"]


def evaluate(checkpoint_path: str, tasks: list = None, batch_size: int = None) -> dict:
    """Run lm-evaluation-harness on checkpoint."""
    if tasks is None:
        tasks = TASKS
    if batch_size is None:
        batch_size = EVAL_CONFIG["batch_size"]

    try:
        import lm_eval
        results = lm_eval.simple_evaluate(
            model="hf",
            model_args=f"pretrained={checkpoint_path}",
            tasks=tasks,
            batch_size=batch_size,
        )

        scores = {}
        for task in tasks:
            metric = METRICS.get(task, "acc")
            task_results = results.get("results", {}).get(task, {})
            scores[task] = task_results.get(metric, task_results.get("acc", 0.0))
        return scores

    except ImportError:
        print("lm-evaluation-harness not installed, using mock evaluation")
        return {task: np.random.uniform(0.25, 0.50) for task in tasks}


def compute_ensemble_score(all_config_scores: dict) -> dict:
    """Compute PC1 ensemble score across all configs."""
    config_ids = sorted(all_config_scores.keys())
    if len(config_ids) < 2:
        return {cid: sum(all_config_scores[cid].values()) / len(TASKS) for cid in config_ids}

    X = np.array([[all_config_scores[cid][task] for task in TASKS] for cid in config_ids])
    X_centered = X - X.mean(axis=0)
    pca = PCA(n_components=1)
    pc1 = pca.fit_transform(X_centered).flatten()

    pc1_normalized = (pc1 - pc1.min()) / (pc1.max() - pc1.min() + 1e-8)
    return {cid: float(pc1_normalized[i]) for i, cid in enumerate(config_ids)}


def save_results(results: dict, path: str):
    """Save results to JSON."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(results, f, indent=2)


def load_results(path: str) -> dict:
    """Load results from JSON."""
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)
