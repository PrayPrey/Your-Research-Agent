"""Main experiment runner: compute response matrix (21 tasks x 6 configs)."""

import gc
import json
import torch
import numpy as np
from pathlib import Path
from tqdm import tqdm
from datetime import datetime

from config import TASKS, COMPRESSION_CONFIGS, MAX_TOKENS
from data import load_task, truncate_sample, build_prompt
from compression import build_model_for_config
from model import generate
from evaluate import score_task


def evaluate_task_with_config(model, tokenizer, task_name: str, task_data, config: dict) -> float:
    """Evaluate a task with given compression config."""
    predictions = []
    references = []

    for sample in tqdm(task_data, desc=f"{task_name}", leave=False):
        sample = truncate_sample(sample, tokenizer, MAX_TOKENS)
        prompt = build_prompt(sample, task_name)
        pred = generate(model, tokenizer, prompt)
        predictions.append(pred)
        references.append(sample.get("answers", sample.get("answer", "")))

    return score_task(task_name, predictions, references)


def compute_response_matrix(tasks: list[str], configs: list[dict]) -> np.ndarray:
    """Compute response matrix (n_tasks x n_configs)."""
    n_tasks = len(tasks)
    n_configs = len(configs)
    matrix = np.zeros((n_tasks, n_configs))

    for j, config in enumerate(configs):
        print(f"\n{'='*60}")
        print(f"Config {j+1}/{n_configs}: {config['name']}")
        print(f"{'='*60}")

        model, tokenizer, h2o_cache = build_model_for_config(config)

        for i, task in enumerate(tasks):
            print(f"\nTask {i+1}/{n_tasks}: {task}")
            task_data = load_task(task)
            acc = evaluate_task_with_config(model, tokenizer, task, task_data, config)
            matrix[i, j] = acc
            print(f"  Score: {acc:.4f}")

        del model
        gc.collect()
        torch.cuda.empty_cache()

    full_config_idx = 0
    for i in range(n_tasks):
        baseline = matrix[i, full_config_idx]
        if baseline > 0:
            matrix[i, :] /= baseline

    return matrix


def main():
    """Run full experiment and save results."""
    base_dir = Path(__file__).parent.parent

    print(f"H-E1 Experiment")
    print(f"Started: {datetime.now().isoformat()}")
    print(f"Tasks: {len(TASKS)}")
    print(f"Configs: {len(COMPRESSION_CONFIGS)}")
    print(f"Total runs: {len(TASKS) * len(COMPRESSION_CONFIGS)}")

    response_matrix = compute_response_matrix(TASKS, COMPRESSION_CONFIGS)

    np.save(base_dir / "response_matrix.npy", response_matrix)
    print(f"\nSaved: response_matrix.npy")

    results = {
        "timestamp": datetime.now().isoformat(),
        "n_tasks": len(TASKS),
        "n_configs": len(COMPRESSION_CONFIGS),
        "tasks": TASKS,
        "configs": [c["name"] for c in COMPRESSION_CONFIGS],
        "response_matrix": response_matrix.tolist(),
    }

    with open(base_dir / "experiment_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved: experiment_results.json")

    print(f"\nCompleted: {datetime.now().isoformat()}")

    return response_matrix


if __name__ == "__main__":
    main()
