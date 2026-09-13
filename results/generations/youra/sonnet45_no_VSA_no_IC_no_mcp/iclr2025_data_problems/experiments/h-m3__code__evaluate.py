"""Evaluate fine-tuned models on MMLU + HellaSwag."""
import subprocess
import json
import yaml
import pandas as pd
from pathlib import Path
from typing import Dict, List


def load_config(config_path: str = "config/experiment_config.yaml") -> dict:
    """Load experiment config."""
    with open(config_path) as f:
        return yaml.safe_load(f)


def run_lm_eval(
    model_path: str,
    tasks: List[str],
    output_path: str,
    batch_size: int = 8,
    num_fewshot: Dict[str, int] = None
) -> Dict[str, float]:
    """
    Run lm-evaluation-harness on checkpoint.
    Returns: {task: accuracy}
    """
    print(f"\nEvaluating {model_path}")

    cmd = [
        "lm_eval",
        "--model", "hf",
        "--model_args", f"pretrained={model_path}",
        "--tasks", ",".join(tasks),
        "--device", "cuda:0",
        "--batch_size", str(batch_size),
        "--output_path", output_path
    ]

    # Add few-shot args if specified
    if num_fewshot:
        for task in tasks:
            if task in num_fewshot:
                cmd.extend(["--num_fewshot", str(num_fewshot[task])])

    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

    # Parse results
    with open(output_path) as f:
        results = json.load(f)

    metrics = {}
    for task in tasks:
        if task == "mmlu":
            metrics[task] = results["results"][task]["acc"]
        elif task == "hellaswag":
            metrics[task] = results["results"][task]["acc_norm"]
        else:
            metrics[task] = results["results"][task].get("acc", 0.0)

    print(f"✓ Results: {metrics}")
    return metrics


def evaluate_all_models(config: dict) -> pd.DataFrame:
    """
    Run MMLU + HellaSwag on 10 models.
    Returns: DataFrame with columns [condition, mmlu, hellaswag, aggregate]
    """
    results = []

    conditions = ["baseline"]
    for stage in ["early", "mid", "late"]:
        for k in config["dataset"]["subset_sizes"]:
            conditions.append(f"{stage}_k{k}")

    for condition in conditions:
        checkpoint_path = f"{config['paths']['models_dir']}{condition}"
        output_path = f"{config['paths']['results_dir']}{condition}.json"

        metrics = run_lm_eval(
            model_path=checkpoint_path,
            tasks=config["evaluation"]["tasks"],
            output_path=output_path,
            batch_size=config["evaluation"]["batch_size"],
            num_fewshot=config["evaluation"]["num_fewshot"]
        )

        results.append({
            "condition": condition,
            "mmlu": metrics["mmlu"],
            "hellaswag": metrics["hellaswag"],
            "aggregate": (metrics["mmlu"] + metrics["hellaswag"]) / 2
        })

    df = pd.DataFrame(results)
    df.to_csv(f"{config['paths']['results_dir']}scores.csv", index=False)
    print(f"\n✓ Saved scores to {config['paths']['results_dir']}scores.csv")

    return df


if __name__ == "__main__":
    config = load_config()
    df = evaluate_all_models(config)

    print("\n=== Evaluation Summary ===")
    print(df.to_string(index=False))

    print(f"\n✓ All models evaluated")
