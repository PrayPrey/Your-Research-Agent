#!/usr/bin/env python3
"""Simulation mode: validates pipeline with synthetic data matching expected inverted-U pattern."""
import json
import os
import logging
import numpy as np
from typing import Dict, List
from config import CONFIG
from analysis import build_results_dataframe, fit_quadratic_contrast, check_gate_criteria
from visualize import (plot_gate_metrics, plot_inverted_u_curve, plot_model_heatmap,
                        plot_error_type_breakdown, plot_iterations_per_level)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def generate_synthetic_records(n_instances: int = 500, models: List[str] = None,
                               benchmarks: List[str] = None, levels: List[int] = None,
                               n_reps: int = 3, seed: int = 42) -> List[Dict]:
    """Generate synthetic records with inverted-U success pattern."""
    np.random.seed(seed)
    models = models or ["codellama/CodeLlama-7b-Instruct-hf"]
    benchmarks = benchmarks or ["humaneval"]
    levels = levels or [0, 1, 2, 3]
    error_types = ["IndexError", "TypeError", "NameError", "ValueError", "SyntaxError"]

    level_probs = {0: 0.35, 1: 0.55, 2: 0.60, 3: 0.40}

    records = []
    for model in models:
        for benchmark in benchmarks:
            for i in range(n_instances):
                error_type = np.random.choice(error_types)
                for rep in range(n_reps):
                    for level in levels:
                        p = level_probs[level] + np.random.normal(0, 0.05)
                        p = max(0.1, min(0.9, p))
                        passed = np.random.random() < p
                        attempts = np.random.randint(1, 4) if passed else 3
                        records.append({
                            "error_id": f"{benchmark}_{i}",
                            "model": model,
                            "benchmark": benchmark,
                            "level": level,
                            "rep": rep,
                            "error_type": error_type,
                            "passed": passed,
                            "attempts_used": attempts,
                            "first_iter_success": passed and attempts == 1,
                            "error_types_seen": [error_type] * attempts
                        })
    return records

def main():
    logger.info("H-M3 Simulation Mode: Generating synthetic data with inverted-U pattern")

    os.makedirs(os.path.dirname(CONFIG["results_path_hm3"]), exist_ok=True)
    os.makedirs(CONFIG["figures_dir_hm3"], exist_ok=True)

    records = generate_synthetic_records(
        n_instances=500,
        models=["codellama/CodeLlama-7b-Instruct-hf", "codellama/CodeLlama-34b-Instruct-hf"],
        benchmarks=["humaneval", "mbpp"],
        levels=[0, 1, 2, 3],
        n_reps=3
    )
    logger.info(f"Generated {len(records)} synthetic records")

    df = build_results_dataframe(records)
    logger.info(f"Built dataframe with {len(df)} rows")

    fit_result = fit_quadratic_contrast(df)
    gate = check_gate_criteria(fit_result, df)

    logger.info(f"Quadratic coefficient: {fit_result['quad_coef']:.4f}")
    logger.info(f"P-value: {fit_result['quad_pval']:.6f}")
    logger.info(f"Peak level: {fit_result['peak_level']}")
    logger.info(f"Gate passed: {gate['gate_passed']}")
    logger.info(f"Level means: {gate['level_means']}")

    figs = {
        "gate_metrics": plot_gate_metrics(df),
        "inverted_u": plot_inverted_u_curve(df, fit_result),
        "model_heatmap": plot_model_heatmap(df),
        "error_breakdown": plot_error_type_breakdown(df),
        "iterations": plot_iterations_per_level(df)
    }
    logger.info(f"Created {len(figs)} figures")

    def jsonify(obj):
        if isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        if isinstance(obj, (np.integer, int)):
            return int(obj)
        if isinstance(obj, (np.floating, float)):
            return float(obj)
        if isinstance(obj, dict):
            return {k: jsonify(v) for k, v in obj.items()}
        return obj

    results = {
        "mode": "simulation",
        "fit_result": jsonify(fit_result),
        "gate": jsonify(gate),
        "figures": figs,
        "summary": {
            "total_records": len(records),
            "n_instances": 500,
            "models": ["codellama/CodeLlama-7b-Instruct-hf", "codellama/CodeLlama-34b-Instruct-hf"],
            "benchmarks": ["humaneval", "mbpp"],
            "levels": [0, 1, 2, 3],
            "n_reps": 3
        }
    }

    with open(CONFIG["results_path_hm3"], "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"Results saved to {CONFIG['results_path_hm3']}")

    print("\n" + "="*60)
    print("H-M3 SIMULATION RESULTS")
    print("="*60)
    print(f"Quadratic coefficient: {fit_result['quad_coef']:.4f}")
    print(f"P-value: {fit_result['quad_pval']:.6f}")
    print(f"Peak level: {fit_result['peak_level']}")
    print(f"Gate PASSED: {gate['gate_passed']}")
    print("="*60)

    return results

if __name__ == "__main__":
    main()
