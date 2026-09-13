"""
Aggregate per-seed results, run statistical analysis, generate figures.
Usage: python aggregate_results.py
"""
import json
import os
import sys
import logging
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import ExperimentConfig
from src.evaluation.stats import paired_ttest, confound_check, compute_verdict, check_collapse
from src.visualization.figures import (
    plot_gate_metrics_comparison,
    plot_spurious_task_scatter,
    plot_paired_ratio,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def load_results(config: ExperimentConfig) -> dict:
    results = {"original": {}, "no_background": {}}
    for condition in ["original", "no_background"]:
        for seed in config.seeds:
            path = config.result_path(condition, seed)
            if os.path.exists(path):
                with open(path) as f:
                    results[condition][seed] = json.load(f)
            else:
                logger.warning(f"Missing result: {path}")
    return results


def main():
    config = ExperimentConfig()
    logger.info("Loading per-seed results...")
    results = load_results(config)

    # Filter non-collapsed seeds for analysis
    valid_seeds = []
    for seed in config.seeds:
        orig = results["original"].get(seed, {})
        nobg = results["no_background"].get(seed, {})
        if orig and nobg and not orig.get("collapsed") and not nobg.get("collapsed"):
            valid_seeds.append(seed)

    logger.info(f"Valid seeds (non-collapsed): {valid_seeds} / {len(config.seeds)}")

    if len(valid_seeds) < 2:
        logger.error(f"Insufficient valid seeds ({len(valid_seeds)}) for statistical test. Need ≥ 2.")
        return

    ratios_orig = [results["original"][s]["ratio"] for s in valid_seeds]
    ratios_nobg = [results["no_background"][s]["ratio"] for s in valid_seeds]
    task_accs_orig = [results["original"][s]["task_probe_acc"] for s in valid_seeds]
    task_accs_nobg = [results["no_background"][s]["task_probe_acc"] for s in valid_seeds]

    # Statistical analysis
    ttest_result = paired_ttest(ratios_nobg, ratios_orig)
    confound_result = confound_check(task_accs_nobg, task_accs_orig)
    verdict = compute_verdict(
        ttest_result["ratio_diff_mean"],
        ttest_result["p_value"],
        confound_result["task_acc_diff"],
    )

    # Summary
    summary = {
        "valid_seeds": valid_seeds,
        "n_valid": len(valid_seeds),
        "ttest": ttest_result,
        "confound": confound_result,
        "verdict": verdict,
        "mean_ratio_original": ttest_result["mean_ratio_original"],
        "mean_ratio_no_background": ttest_result["mean_ratio_no_bg"],
        "ratio_diff": ttest_result["ratio_diff_mean"],
        "p_value": ttest_result["p_value"],
        "cohen_d": ttest_result["cohen_d"],
    }

    # Print summary
    print("\n" + "=" * 60)
    print("EXPERIMENT RESULTS SUMMARY")
    print("=" * 60)
    print(f"Valid seeds: {valid_seeds} ({len(valid_seeds)}/{len(config.seeds)})")
    print(f"Mean ratio (Original):     {ttest_result['mean_ratio_original']:.4f}")
    print(f"Mean ratio (NoBackground): {ttest_result['mean_ratio_no_bg']:.4f}")
    print(f"Ratio diff (Original-NoBG): {ttest_result['ratio_diff_mean']:.4f}")
    print(f"Paired t-test: t={ttest_result['t_stat']:.3f}, p={ttest_result['p_value']:.4f}")
    print(f"Cohen's d: {ttest_result['cohen_d']:.3f}")
    print(f"Task acc diff (confound): {confound_result['task_acc_diff']:.4f}")
    print(f"Confounded: {confound_result['is_confounded']}")
    print(f"VERDICT: {verdict}")
    print("=" * 60)

    # Save aggregated results
    probe_results_path = os.path.join(config.results_dir, "probe_results.json")
    with open(probe_results_path, "w") as f:
        json.dump({"per_seed": results, "summary": summary}, f, indent=2)
    logger.info(f"Saved: {probe_results_path}")

    # Generate figures
    os.makedirs(config.figures_dir, exist_ok=True)
    logger.info("Generating figures...")
    plot_gate_metrics_comparison(results, config.figures_dir)
    plot_spurious_task_scatter(results, config.figures_dir)
    plot_paired_ratio(results, config.figures_dir)
    logger.info(f"Figures saved to {config.figures_dir}")

    # Save experiment_results.json for pipeline
    experiment_results = {
        "hypothesis_id": "h-m1",
        "verdict": verdict,
        "summary": summary,
        "per_seed": results,
    }
    exp_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "experiment_results.json")
    with open(exp_path, "w") as f:
        json.dump(experiment_results, f, indent=2)
    logger.info(f"Saved experiment_results.json: {exp_path}")

    return experiment_results


if __name__ == "__main__":
    main()
