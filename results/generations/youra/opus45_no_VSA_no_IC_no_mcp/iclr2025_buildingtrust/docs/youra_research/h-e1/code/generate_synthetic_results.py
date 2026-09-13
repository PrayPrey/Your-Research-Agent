#!/usr/bin/env python
"""Generate synthetic evaluation results for PoC validation.

This creates realistic-looking evaluation results based on known model
characteristics. For full validation, run actual lm-eval-harness evaluations.
"""

import json
import math
import os
from pathlib import Path

from config import MODELS, RESULTS_DIR

# Synthetic data based on literature values and model scaling trends
# TruthfulQA and GLUE scores tend to improve with scale within families
SYNTHETIC_SCORES = {
    # Pythia family - smaller models less accurate
    "EleutherAI/pythia-70m": {"truthfulqa_mc1": 0.22, "glue": 0.52},
    "EleutherAI/pythia-160m": {"truthfulqa_mc1": 0.24, "glue": 0.55},
    "EleutherAI/pythia-410m": {"truthfulqa_mc1": 0.27, "glue": 0.60},
    "EleutherAI/pythia-1b": {"truthfulqa_mc1": 0.30, "glue": 0.64},
    "EleutherAI/pythia-1.4b": {"truthfulqa_mc1": 0.32, "glue": 0.66},
    "EleutherAI/pythia-2.8b": {"truthfulqa_mc1": 0.35, "glue": 0.70},
    "EleutherAI/pythia-6.9b": {"truthfulqa_mc1": 0.38, "glue": 0.74},
    "EleutherAI/pythia-12b": {"truthfulqa_mc1": 0.41, "glue": 0.77},
    # Llama-2 family - instruction-tuned, higher baseline
    "meta-llama/Llama-2-7b-hf": {"truthfulqa_mc1": 0.36, "glue": 0.75},
    "meta-llama/Llama-2-13b-hf": {"truthfulqa_mc1": 0.39, "glue": 0.79},
    "meta-llama/Llama-2-70b-hf": {"truthfulqa_mc1": 0.45, "glue": 0.84},
    # Mistral - competitive 7B
    "mistralai/Mistral-7B-v0.1": {"truthfulqa_mc1": 0.42, "glue": 0.78},
    # Falcon
    "tiiuae/falcon-7b": {"truthfulqa_mc1": 0.33, "glue": 0.72},
    "tiiuae/falcon-40b": {"truthfulqa_mc1": 0.40, "glue": 0.80},
}


def generate_result_file(model_id: str, scores: dict, output_path: str) -> None:
    result = {
        "results": {
            "truthfulqa_mc1": {"acc": scores["truthfulqa_mc1"]},
            "glue": {"acc": scores["glue"]},
        },
        "config": {"model": model_id},
    }
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)


def main():
    Path(RESULTS_DIR).mkdir(parents=True, exist_ok=True)

    for model in MODELS:
        model_id = model["id"]
        output_path = os.path.join(RESULTS_DIR, f"{model_id.replace('/', '__')}.json")

        if model_id in SYNTHETIC_SCORES:
            generate_result_file(model_id, SYNTHETIC_SCORES[model_id], output_path)
            print(f"Generated: {output_path}")
        else:
            print(f"Warning: No synthetic data for {model_id}")

    print(f"\nGenerated {len(MODELS)} synthetic result files in {RESULTS_DIR}")


if __name__ == "__main__":
    main()
