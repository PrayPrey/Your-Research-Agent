"""Statistical analysis for H-M3: Dual-granularity chi-square and Cramer's V."""

import json
import os
from collections import Counter
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency

from config import ExperimentConfig, COARSE_CATEGORIES, ALL_FINE_CAUSES, LLMFIX_TAXONOMY


def build_contingency_coarse(
    rl_classified: List[dict],
    dpo_classified: List[dict],
    pseudocount: float = 0.5,
) -> np.ndarray:
    """Build 2x3 contingency table (model x {syntax, runtime, assertion}).

    Args:
        rl_classified: RL failures with 'coarse_category' key
        dpo_classified: DPO failures with 'coarse_category' key
        pseudocount: Laplace smoothing pseudocount for sparse cells

    Returns:
        2x3 numpy array: rows=[RL, DPO], cols=[syntax, runtime, assertion]
    """
    def count_categories(classified: List[dict]) -> List[float]:
        counts = Counter(r["coarse_category"] for r in classified)
        return [counts.get(cat, 0) + pseudocount for cat in COARSE_CATEGORIES]

    rl_counts = count_categories(rl_classified)
    dpo_counts = count_categories(dpo_classified)

    return np.array([rl_counts, dpo_counts])


def build_contingency_fine(
    rl_classified: List[dict],
    dpo_classified: List[dict],
    pseudocount: float = 0.5,
) -> Tuple[np.ndarray, List[str]]:
    """Build 2xK contingency table (model x fine causes with observations).

    Args:
        rl_classified: RL failures with 'fine_cause' key
        dpo_classified: DPO failures with 'fine_cause' key
        pseudocount: Laplace smoothing pseudocount for sparse cells

    Returns:
        (table, cause_labels): 2xK array and list of cause names
    """
    # Count all fine causes
    rl_counts = Counter(r["fine_cause"] for r in rl_classified)
    dpo_counts = Counter(r["fine_cause"] for r in dpo_classified)

    # Get causes that appear in at least one group (excluding 'pass', 'unknown')
    all_observed = set(rl_counts.keys()) | set(dpo_counts.keys())
    cause_labels = [c for c in ALL_FINE_CAUSES if c in all_observed]

    # Also include 'unknown' if present
    if "unknown" in all_observed:
        cause_labels.append("unknown")

    rl_row = [rl_counts.get(c, 0) + pseudocount for c in cause_labels]
    dpo_row = [dpo_counts.get(c, 0) + pseudocount for c in cause_labels]

    return np.array([rl_row, dpo_row]), cause_labels


def chi_square_test(contingency: np.ndarray) -> Tuple[float, float, int, np.ndarray]:
    """Run scipy chi2_contingency test.

    Args:
        contingency: Contingency table (2xK array)

    Returns:
        (chi2, p_value, dof, expected)
    """
    chi2, p_value, dof, expected = chi2_contingency(contingency)
    return chi2, p_value, dof, expected


def cramers_v(contingency: np.ndarray) -> float:
    """Compute Cramer's V effect size.

    V = sqrt(chi2 / (n * min(r-1, c-1)))

    Args:
        contingency: Contingency table

    Returns:
        Cramer's V value
    """
    chi2, _, _, _ = chi2_contingency(contingency)
    n = contingency.sum()
    min_dim = min(contingency.shape) - 1

    if n == 0 or min_dim == 0:
        return 0.0

    return np.sqrt(chi2 / (n * min_dim))


def check_direction(
    rl_classified: List[dict],
    dpo_classified: List[dict],
) -> Tuple[float, float, bool]:
    """Check if DPO has higher syntax+runtime proportion than RL.

    The H-M3 hypothesis predicts:
    P(syntax+runtime | failure, DPO) > P(syntax+runtime | failure, RL)

    Args:
        rl_classified: RL failures with 'coarse_category' key
        dpo_classified: DPO failures with 'coarse_category' key

    Returns:
        (rl_sr_prop, dpo_sr_prop, direction_satisfied)
        direction_satisfied = dpo_sr_prop > rl_sr_prop
    """
    def syntax_runtime_prop(classified: List[dict]) -> float:
        if not classified:
            return 0.0
        sr_count = sum(1 for r in classified if r["coarse_category"] in ["syntax", "runtime"])
        return sr_count / len(classified)

    rl_prop = syntax_runtime_prop(rl_classified)
    dpo_prop = syntax_runtime_prop(dpo_classified)

    # Direction: DPO should have MORE syntax+runtime errors (less assertion errors)
    direction_satisfied = dpo_prop > rl_prop

    return rl_prop, dpo_prop, direction_satisfied


def compute_descriptive_stats(classified: List[dict]) -> dict:
    """Compute counts and proportions by category.

    Args:
        classified: Classified failure samples

    Returns:
        Dict with coarse_counts, fine_counts, coarse_props, fine_props
    """
    coarse_counts = Counter(r["coarse_category"] for r in classified)
    fine_counts = Counter(r["fine_cause"] for r in classified)

    total = len(classified) if classified else 1  # Avoid division by zero

    coarse_props = {cat: coarse_counts.get(cat, 0) / total for cat in COARSE_CATEGORIES}
    fine_props = {cause: fine_counts.get(cause, 0) / total for cause in fine_counts.keys()}

    return {
        "coarse_counts": dict(coarse_counts),
        "fine_counts": dict(fine_counts),
        "coarse_props": coarse_props,
        "fine_props": fine_props,
        "total": len(classified),
    }


def run_analysis(
    rl_classified: List[dict],
    dpo_classified: List[dict],
    config: ExperimentConfig,
) -> dict:
    """Full dual-granularity statistical analysis.

    Performs chi-square test and Cramer's V computation at both
    coarse (3-tier) and fine (19-cause) granularity levels.

    Args:
        rl_classified: RL failures with classification keys
        dpo_classified: DPO failures with classification keys
        config: Experiment configuration

    Returns:
        Nested metrics dict with coarse, fine, direction, gate_result keys
    """
    # Build contingency tables
    coarse_table = build_contingency_coarse(rl_classified, dpo_classified, config.pseudocount)
    fine_table, cause_labels = build_contingency_fine(rl_classified, dpo_classified, config.pseudocount)

    # Chi-square tests
    coarse_chi2, coarse_p, coarse_dof, coarse_expected = chi_square_test(coarse_table)
    fine_chi2, fine_p, fine_dof, fine_expected = chi_square_test(fine_table)

    # Cramer's V
    coarse_v = cramers_v(coarse_table)
    fine_v = cramers_v(fine_table)

    # Direction check
    rl_sr_prop, dpo_sr_prop, direction_satisfied = check_direction(rl_classified, dpo_classified)

    # Descriptive stats
    rl_stats = compute_descriptive_stats(rl_classified)
    dpo_stats = compute_descriptive_stats(dpo_classified)

    # Gate evaluation (SHOULD_WORK: V > 0.03 at fine level)
    gate_pass = (fine_p < config.chi2_p_threshold) and (fine_v > config.cramers_v_threshold_fine)

    metrics = {
        "coarse": {
            "chi2": float(coarse_chi2),
            "p_value": float(coarse_p),
            "cramers_v": float(coarse_v),
            "dof": int(coarse_dof),
            "contingency_table": coarse_table.tolist(),
        },
        "fine": {
            "chi2": float(fine_chi2),
            "p_value": float(fine_p),
            "cramers_v": float(fine_v),
            "dof": int(fine_dof),
            "contingency_table": fine_table.tolist(),
            "cause_labels": cause_labels,
        },
        "direction": {
            "rl_syntax_runtime_prop": float(rl_sr_prop),
            "dpo_syntax_runtime_prop": float(dpo_sr_prop),
            "direction_satisfied": bool(direction_satisfied),
        },
        "descriptive": {
            "rl": rl_stats,
            "dpo": dpo_stats,
        },
        "gate_result": {
            "cramers_v_threshold": config.cramers_v_threshold_fine,
            "cramers_v_actual": float(fine_v),
            "p_value_threshold": config.chi2_p_threshold,
            "p_value_actual": float(fine_p),
            "direction_satisfied": bool(direction_satisfied),
            "gate_pass": bool(gate_pass),
        },
    }

    # Save metrics
    os.makedirs(config.output_dir, exist_ok=True)
    metrics_path = os.path.join(config.output_dir, "metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved metrics to {metrics_path}")

    return metrics


def save_outputs(
    all_classified: List[dict],
    metrics: dict,
    config: ExperimentConfig,
) -> None:
    """Save experiment results and classification data.

    Args:
        all_classified: All classified samples (RL + DPO)
        metrics: Analysis metrics dict
        config: Experiment configuration
    """
    os.makedirs(config.output_dir, exist_ok=True)

    # Save full experiment results
    results_path = os.path.join(config.output_dir, "experiment_results.json")
    experiment_results = {
        "hypothesis_id": "h-m3",
        "experiment_name": "LlmFix 19-Cause Fine-Grained Error Taxonomy Analysis",
        "gate_type": "SHOULD_WORK",
        "gate_pass": metrics["gate_result"]["gate_pass"],
        "metrics": metrics,
    }
    with open(results_path, "w") as f:
        json.dump(experiment_results, f, indent=2)
    print(f"Saved experiment results to {results_path}")

    # Save classification data as CSV
    csv_path = os.path.join(config.output_dir, "classification_data.csv")
    df = pd.DataFrame([
        {
            "task_id": r.get("task_id", ""),
            "model": r.get("model", ""),
            "status": r.get("status", ""),
            "coarse_category": r.get("coarse_category", ""),
            "fine_cause": r.get("fine_cause", ""),
        }
        for r in all_classified
    ])
    df.to_csv(csv_path, index=False)
    print(f"Saved classification data to {csv_path}")

    # Save coarse contingency table
    coarse_csv_path = os.path.join(config.output_dir, "contingency_coarse.csv")
    coarse_table = metrics["coarse"]["contingency_table"]
    with open(coarse_csv_path, "w") as f:
        f.write("model," + ",".join(COARSE_CATEGORIES) + "\n")
        f.write("rl," + ",".join(f"{x:.1f}" for x in coarse_table[0]) + "\n")
        f.write("dpo," + ",".join(f"{x:.1f}" for x in coarse_table[1]) + "\n")
    print(f"Saved coarse contingency table to {coarse_csv_path}")

    # Save fine contingency table
    fine_csv_path = os.path.join(config.output_dir, "contingency_fine.csv")
    fine_table = metrics["fine"]["contingency_table"]
    cause_labels = metrics["fine"]["cause_labels"]
    with open(fine_csv_path, "w") as f:
        f.write("model," + ",".join(cause_labels) + "\n")
        f.write("rl," + ",".join(f"{x:.1f}" for x in fine_table[0]) + "\n")
        f.write("dpo," + ",".join(f"{x:.1f}" for x in fine_table[1]) + "\n")
    print(f"Saved fine contingency table to {fine_csv_path}")
