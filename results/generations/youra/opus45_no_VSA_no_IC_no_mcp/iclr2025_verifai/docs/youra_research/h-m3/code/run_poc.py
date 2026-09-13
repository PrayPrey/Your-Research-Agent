#!/usr/bin/env python3
import json
import os
import logging
import argparse
from typing import Dict, List
from config import CONFIG
from experiment import collect_error_instances, run_level_sweep
from analysis import build_results_dataframe, fit_quadratic_contrast, check_gate_criteria
from visualize import (plot_gate_metrics, plot_inverted_u_curve, plot_model_heatmap,
                        plot_error_type_breakdown, plot_iterations_per_level)

logging.basicConfig(
    level=getattr(logging, CONFIG["log_level"]),
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(CONFIG["log_path"]),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main(models: List[str] = None, benchmarks: List[str] = None,
         levels: List[int] = None, n_reps: int = None,
         target_instances: int = None):
    models = models or CONFIG["models"]
    benchmarks = benchmarks or CONFIG["benchmarks"]
    levels = levels or CONFIG["fix_levels"]
    n_reps = n_reps or CONFIG["n_repetitions"]
    target = target_instances or CONFIG["target_error_instances"]

    os.makedirs(os.path.dirname(CONFIG["results_path_hm3"]), exist_ok=True)
    os.makedirs(CONFIG["figures_dir_hm3"], exist_ok=True)

    all_records = []
    all_instances = {}

    for model_name in models:
        for benchmark in benchmarks:
            logger.info(f"Stage 1: Collecting errors for {model_name} on {benchmark}")
            instances = collect_error_instances(model_name, benchmark)
            all_instances[f"{model_name}_{benchmark}"] = len(instances)
            logger.info(f"  Collected {len(instances)} error instances")

            logger.info(f"Stage 2: Running level sweep for {model_name} on {benchmark}")
            records = run_level_sweep(model_name, benchmark, levels, n_reps,
                                      error_instances=instances)
            all_records.extend(records)
            logger.info(f"  Completed {len(records)} repair attempts")

    logger.info("Stage 3: Building results dataframe and fitting model")
    df = build_results_dataframe(all_records)
    fit_result = fit_quadratic_contrast(df)
    gate = check_gate_criteria(fit_result, df)

    logger.info(f"  Quadratic coefficient: {fit_result['quad_coef']:.4f}")
    logger.info(f"  P-value: {fit_result['quad_pval']:.4f}")
    logger.info(f"  Peak level: {fit_result['peak_level']}")
    logger.info(f"  Gate passed: {gate['gate_passed']}")

    logger.info("Stage 4: Generating visualizations")
    figs = {
        "gate_metrics": plot_gate_metrics(df),
        "inverted_u": plot_inverted_u_curve(df, fit_result),
        "model_heatmap": plot_model_heatmap(df),
        "error_breakdown": plot_error_type_breakdown(df),
        "iterations": plot_iterations_per_level(df)
    }
    logger.info(f"  Created {len(figs)} figures")

    results = {
        "fit_result": {k: float(v) if isinstance(v, (int, float)) else v
                       for k, v in fit_result.items()},
        "gate": gate,
        "figures": figs,
        "summary": {
            "total_records": len(all_records),
            "models": models,
            "benchmarks": benchmarks,
            "levels": levels,
            "n_reps": n_reps,
            "instances_per_config": all_instances
        }
    }

    with open(CONFIG["results_path_hm3"], "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"Results saved to {CONFIG['results_path_hm3']}")

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="H-M3: Fix Specificity Inverted-U Experiment")
    parser.add_argument("--models", nargs="+", default=None)
    parser.add_argument("--benchmarks", nargs="+", default=None)
    parser.add_argument("--levels", nargs="+", type=int, default=None)
    parser.add_argument("--n_reps", type=int, default=None)
    parser.add_argument("--target_instances", type=int, default=None)
    args = parser.parse_args()

    main(models=args.models, benchmarks=args.benchmarks,
         levels=args.levels, n_reps=args.n_reps,
         target_instances=args.target_instances)
