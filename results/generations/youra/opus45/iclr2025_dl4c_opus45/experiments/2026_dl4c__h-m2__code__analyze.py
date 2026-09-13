"""H-M2 Statistical Analysis: t-test for execution depth comparison."""

import csv
import json
import logging
import os
from typing import Dict, List, Tuple

import numpy as np
from scipy import stats

from config import HM2Config
from depth_tracer import DepthResult

logger = logging.getLogger(__name__)


def run_ttest(
    rl_depths: List[float],
    dpo_depths: List[float],
    alternative: str = "greater",
) -> Tuple[float, float]:
    """Run independent samples t-test (Welch's t-test).

    Args:
        rl_depths: Execution depths for RL failures
        dpo_depths: Execution depths for DPO failures
        alternative: "greater" for one-sided (RL > DPO)

    Returns:
        Tuple of (t_statistic, p_value)
    """
    # Use Welch's t-test (unequal variances)
    t_stat, p_two = stats.ttest_ind(rl_depths, dpo_depths, equal_var=False)

    # Convert to one-sided p-value
    if alternative == "greater":
        # We want P(T > t_stat) = RL mean > DPO mean
        if t_stat > 0:
            p_one = p_two / 2
        else:
            p_one = 1 - p_two / 2
    elif alternative == "less":
        if t_stat < 0:
            p_one = p_two / 2
        else:
            p_one = 1 - p_two / 2
    else:
        p_one = p_two  # two-sided

    return float(t_stat), float(p_one)


def compute_cohens_d(
    rl_depths: List[float],
    dpo_depths: List[float],
) -> float:
    """Compute Cohen's d effect size with pooled standard deviation.

    Args:
        rl_depths: Execution depths for RL failures
        dpo_depths: Execution depths for DPO failures

    Returns:
        Cohen's d: (mean_rl - mean_dpo) / pooled_std
    """
    n1, n2 = len(rl_depths), len(dpo_depths)
    mean1, mean2 = np.mean(rl_depths), np.mean(dpo_depths)
    var1, var2 = np.var(rl_depths, ddof=1), np.var(dpo_depths, ddof=1)

    # Pooled standard deviation
    pooled_var = ((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2)
    pooled_std = np.sqrt(pooled_var)

    # Avoid division by zero
    if pooled_std < 1e-10:
        return 0.0

    return float((mean1 - mean2) / pooled_std)


def compute_descriptive_stats(depths: List[float]) -> Dict:
    """Compute descriptive statistics for depth values.

    Args:
        depths: List of execution depth values

    Returns:
        Dict with mean, std, median, min, max, n, ci_lower, ci_upper (95% CI)
    """
    arr = np.array(depths)
    n = len(arr)
    mean = float(np.mean(arr))
    std = float(np.std(arr, ddof=1)) if n > 1 else 0.0
    median = float(np.median(arr))

    # 95% confidence interval
    if n > 1 and std > 0:
        se = std / np.sqrt(n)
        ci_half = 1.96 * se
        ci_lower = mean - ci_half
        ci_upper = mean + ci_half
    else:
        ci_lower = mean
        ci_upper = mean

    return {
        "mean": mean,
        "std": std,
        "median": median,
        "min": float(np.min(arr)) if n > 0 else 0.0,
        "max": float(np.max(arr)) if n > 0 else 0.0,
        "n": n,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
    }


def run_analysis(
    rl_results: List[DepthResult],
    dpo_results: List[DepthResult],
    config: HM2Config,
) -> Dict:
    """Run full statistical analysis pipeline.

    Args:
        rl_results: DepthResult list for RL failures
        dpo_results: DepthResult list for DPO failures
        config: H-M2 configuration

    Returns:
        Metrics dict with all statistics and gate pass status
    """
    # Extract depth values
    rl_depths = [r.execution_depth for r in rl_results]
    dpo_depths = [r.execution_depth for r in dpo_results]

    # Statistical tests
    t_stat, p_value = run_ttest(rl_depths, dpo_depths, config.alternative)
    cohens_d = compute_cohens_d(rl_depths, dpo_depths)

    # Descriptive stats
    rl_stats = compute_descriptive_stats(rl_depths)
    dpo_stats = compute_descriptive_stats(dpo_depths)

    # Gate pass logic: p < threshold AND mean(RL) > mean(DPO)
    gate_pass = (p_value < config.t_test_p_threshold) and (rl_stats["mean"] > dpo_stats["mean"])

    metrics = {
        "hypothesis": "H-M2",
        "gate_type": "SHOULD_WORK",
        "gate_pass": gate_pass,
        "t_statistic": t_stat,
        "p_value": p_value,
        "p_threshold": config.t_test_p_threshold,
        "cohens_d": cohens_d,
        "rl_statistics": rl_stats,
        "dpo_statistics": dpo_stats,
        "direction_correct": rl_stats["mean"] > dpo_stats["mean"],
        "trace_success_rate": {
            "rl": sum(1 for r in rl_results if r.trace_success) / len(rl_results) if rl_results else 0.0,
            "dpo": sum(1 for r in dpo_results if r.trace_success) / len(dpo_results) if dpo_results else 0.0,
        },
    }

    # Log key results
    logger.info(f"=== H-M2 Analysis Results ===")
    logger.info(f"RL mean depth: {rl_stats['mean']:.4f} (n={rl_stats['n']})")
    logger.info(f"DPO mean depth: {dpo_stats['mean']:.4f} (n={dpo_stats['n']})")
    logger.info(f"t-statistic: {t_stat:.4f}")
    logger.info(f"p-value (one-sided): {p_value:.6f}")
    logger.info(f"Cohen's d: {cohens_d:.4f}")
    logger.info(f"Gate pass: {gate_pass}")

    # Save outputs
    save_outputs(rl_results, dpo_results, metrics, config)

    return metrics


def save_outputs(
    rl_results: List[DepthResult],
    dpo_results: List[DepthResult],
    metrics: Dict,
    config: HM2Config,
) -> None:
    """Save all output files.

    Args:
        rl_results: DepthResult list for RL failures
        dpo_results: DepthResult list for DPO failures
        metrics: Analysis metrics dict
        config: H-M2 configuration
    """
    os.makedirs(config.output_dir, exist_ok=True)

    # Save metrics.json
    metrics_path = os.path.join(config.output_dir, "metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    logger.info(f"Saved metrics to {metrics_path}")

    # Save experiment_results.json
    experiment_results = {
        "hypothesis": "H-M2",
        "rl_results": [
            {
                "sample_id": r.sample_id,
                "model": r.model,
                "problem_id": r.problem_id,
                "total_lines": r.total_lines,
                "executed_lines": r.executed_lines,
                "execution_depth": r.execution_depth,
                "error_type": r.error_type,
                "trace_success": r.trace_success,
            }
            for r in rl_results
        ],
        "dpo_results": [
            {
                "sample_id": r.sample_id,
                "model": r.model,
                "problem_id": r.problem_id,
                "total_lines": r.total_lines,
                "executed_lines": r.executed_lines,
                "execution_depth": r.execution_depth,
                "error_type": r.error_type,
                "trace_success": r.trace_success,
            }
            for r in dpo_results
        ],
        "metrics": metrics,
    }
    results_path = os.path.join(config.output_dir, "experiment_results.json")
    with open(results_path, "w") as f:
        json.dump(experiment_results, f, indent=2)
    logger.info(f"Saved experiment results to {results_path}")

    # Save depth_data.csv
    csv_path = os.path.join(config.output_dir, "depth_data.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["sample_id", "model", "problem_id", "total_lines", "executed_lines", "depth", "error_type"])
        for r in rl_results + dpo_results:
            writer.writerow([
                r.sample_id, r.model, r.problem_id,
                r.total_lines, r.executed_lines, r.execution_depth, r.error_type
            ])
    logger.info(f"Saved depth data to {csv_path}")
