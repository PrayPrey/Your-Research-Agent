"""Aggregate lm-eval-harness results into scores DataFrame."""

import json
import math
import os
from pathlib import Path

import pandas as pd

from config import MODELS, RESULTS_DIR, SCORES_CSV


def sanitize_model_id(model_id: str) -> str:
    return model_id.replace("/", "__")


def parse_result_file(path: str) -> dict:
    with open(path) as f:
        data = json.load(f)

    results = data.get("results", {})

    truthfulqa_mc1 = None
    if "truthfulqa_mc1" in results:
        truthfulqa_mc1 = results["truthfulqa_mc1"].get("acc", 0.0)
    elif "truthfulqa" in results:
        truthfulqa_mc1 = results["truthfulqa"].get("mc1", 0.0)

    glue_scores = []
    for task_name, task_results in results.items():
        if task_name.startswith("glue_") or task_name == "glue":
            acc = task_results.get("acc", task_results.get("accuracy", 0.0))
            if acc:
                glue_scores.append(acc)

    advglue_avg = sum(glue_scores) / len(glue_scores) if glue_scores else 0.0

    return {"truthfulqa_mc1": truthfulqa_mc1 or 0.0, "advglue_avg": advglue_avg}


def collect_scores(models: list = None, results_dir: str = None) -> pd.DataFrame:
    models = models or MODELS
    results_dir = results_dir or RESULTS_DIR

    rows = []
    for model in models:
        model_id = model["id"]
        result_path = os.path.join(results_dir, f"{sanitize_model_id(model_id)}.json")

        if not os.path.exists(result_path):
            print(f"Missing results for {model_id}")
            continue

        scores = parse_result_file(result_path)
        rows.append({
            "model": model_id,
            "family": model["family"],
            "params": model["params"],
            "log_params": math.log10(model["params"]),
            "truthfulqa_mc1": scores["truthfulqa_mc1"],
            "advglue_avg": scores["advglue_avg"],
        })

    return pd.DataFrame(rows)


def save_scores(df: pd.DataFrame, path: str = None) -> None:
    path = path or SCORES_CSV
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Saved scores to {path}")


if __name__ == "__main__":
    df = collect_scores()
    save_scores(df)
    print(df)
