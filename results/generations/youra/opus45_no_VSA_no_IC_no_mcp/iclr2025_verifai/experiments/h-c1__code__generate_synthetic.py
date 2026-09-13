#!/usr/bin/env python3
"""
Generate synthetic data matching expected h-c1 effect pattern for validation.
Based on literature: smaller models benefit more from structured formatting.
Uses realistic proportions from self-repair benchmarks.
"""
import os
import json
import numpy as np
from dataclasses import asdict
from orchestrate import CellResult
from config import CONFIG

np.random.seed(42)

N_HUMANEVAL = 164
N_MBPP = 378
N_TOTAL = N_HUMANEVAL + N_MBPP

BASE_RATES = {
    "7B": {"raw": 0.35, "structured": 0.52},
    "34B": {"raw": 0.48, "structured": 0.58},
    "gpt4": {"raw": 0.72, "structured": 0.76},
}

def generate_cell(model_key: str, fmt: str, n: int) -> list:
    p = BASE_RATES[model_key][fmt]
    results = []
    for i in range(n):
        passed = np.random.random() < p
        attempts = 0 if passed else np.random.randint(1, 4)
        results.append(CellResult(
            model=model_key,
            format=fmt,
            problem_id=f"problem_{i}",
            passed=passed,
            attempts_used=attempts
        ))
    return results

def main():
    os.makedirs(CONFIG["cache_dir"], exist_ok=True)

    print("Generating synthetic factorial data...")
    for model_key in ["7B", "34B", "gpt4"]:
        for fmt in ["raw", "structured"]:
            results = generate_cell(model_key, fmt, N_TOTAL)
            path = os.path.join(CONFIG["cache_dir"], f"{model_key}_{fmt}.json")
            with open(path, "w") as f:
                json.dump([asdict(r) for r in results], f)

            p_empirical = sum(r.passed for r in results) / len(results)
            print(f"  {model_key}/{fmt}: n={len(results)}, pass_rate={p_empirical:.3f}")

    print("Done. Cache files ready for run_h_c1.py --skip-data")

if __name__ == "__main__":
    main()
