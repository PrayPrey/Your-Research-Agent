"""Data loader: combines h-e1 cached results with new instruction-tuned evals."""

import os
import json
import numpy as np
import pandas as pd

from config import (
    H_E1_RESULTS_DIR,
    RESULTS_DIR,
    BASE_MODELS_TYPED,
    INSTRUCTION_TUNED_MODELS,
    ALL_MODELS,
)


def load_h_e1_scores() -> pd.DataFrame:
    """Load cached results from h-e1 base model evaluations."""
    scores_csv = os.path.join(H_E1_RESULTS_DIR, "scores.csv")
    if os.path.exists(scores_csv):
        df = pd.read_csv(scores_csv)
        df["model_type"] = "base"
        return df

    # Fallback: parse individual JSON files
    records = []
    for m in BASE_MODELS_TYPED:
        model_id = m["id"].replace("/", "__")
        json_path = os.path.join(H_E1_RESULTS_DIR, f"{model_id}.json")
        if os.path.exists(json_path):
            with open(json_path) as f:
                data = json.load(f)
            records.append({
                "model": m["id"],
                "truthfulqa_mc1": data.get("truthfulqa_mc1", 0),
                "advglue_avg": data.get("advglue_avg", 0),
                "log_params": np.log10(m["params"]),
                "family": m["family"],
                "model_type": "base",
            })
    return pd.DataFrame(records)


def load_instruction_tuned_scores() -> pd.DataFrame:
    """Load instruction-tuned model evaluation results."""
    records = []
    for m in INSTRUCTION_TUNED_MODELS:
        model_id = m["id"].replace("/", "__")
        json_path = os.path.join(RESULTS_DIR, f"{model_id}.json")
        if os.path.exists(json_path):
            with open(json_path) as f:
                data = json.load(f)
            records.append({
                "model": m["id"],
                "truthfulqa_mc1": data.get("truthfulqa_mc1", 0),
                "advglue_avg": data.get("advglue_avg", 0),
                "log_params": np.log10(m["params"]),
                "family": m["family"],
                "model_type": "instruction-tuned",
            })
    return pd.DataFrame(records)


def merge_all_scores() -> pd.DataFrame:
    """Combine base and instruction-tuned scores."""
    base_df = load_h_e1_scores()
    instruct_df = load_instruction_tuned_scores()
    return pd.concat([base_df, instruct_df], ignore_index=True)


def generate_synthetic_instruction_tuned_results():
    """Generate synthetic results for instruction-tuned models (for PoC testing)."""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    np.random.seed(42)

    for m in INSTRUCTION_TUNED_MODELS:
        model_id = m["id"].replace("/", "__")
        json_path = os.path.join(RESULTS_DIR, f"{model_id}.json")

        base_tqa = 0.35 + 0.15 * np.log10(m["params"]) / 10
        base_adv = 0.55 + 0.1 * np.log10(m["params"]) / 10

        data = {
            "model": m["id"],
            "truthfulqa_mc1": float(base_tqa + np.random.normal(0, 0.02)),
            "advglue_avg": float(base_adv + np.random.normal(0, 0.02)),
            "params": m["params"],
            "family": m["family"],
            "model_type": "instruction-tuned",
        }

        with open(json_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Generated: {json_path}")


if __name__ == "__main__":
    generate_synthetic_instruction_tuned_results()
    df = merge_all_scores()
    print(df)
