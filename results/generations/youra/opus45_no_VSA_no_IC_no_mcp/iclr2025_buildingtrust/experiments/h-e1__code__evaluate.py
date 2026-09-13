"""Evaluation pipeline using lm-evaluation-harness."""

import json
import os
import subprocess
from pathlib import Path

from config import MODELS, TASKS, RESULTS_DIR


def sanitize_model_id(model_id: str) -> str:
    return model_id.replace("/", "__")


def result_exists(output_path: str) -> bool:
    if not os.path.exists(output_path):
        return False
    try:
        with open(output_path) as f:
            json.load(f)
        return True
    except (json.JSONDecodeError, IOError):
        return False


def run_lm_eval(model_id: str, tasks: list, output_path: str) -> None:
    tasks_str = ",".join(tasks)
    cmd = [
        "lm_eval",
        "--model", "hf",
        "--model_args", f"pretrained={model_id}",
        "--tasks", tasks_str,
        "--batch_size", "auto",
        "--output_path", output_path,
    ]
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def evaluate_all(models: list = None, tasks: list = None, results_dir: str = None) -> None:
    models = models or MODELS
    tasks = tasks or TASKS
    results_dir = results_dir or RESULTS_DIR

    Path(results_dir).mkdir(parents=True, exist_ok=True)

    for model in models:
        model_id = model["id"]
        output_path = os.path.join(results_dir, f"{sanitize_model_id(model_id)}.json")

        if result_exists(output_path):
            print(f"Skipping {model_id} (cached)")
            continue

        print(f"Evaluating {model_id}...")
        try:
            run_lm_eval(model_id, tasks, output_path)
            print(f"Completed {model_id}")
        except subprocess.CalledProcessError as e:
            print(f"Failed {model_id}: {e}")


if __name__ == "__main__":
    evaluate_all()
