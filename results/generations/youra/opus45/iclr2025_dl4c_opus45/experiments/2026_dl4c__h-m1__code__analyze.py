"""H-M1 Fisher Analysis: Zero-Reward Basin Mechanism Test.

Tests: P(assertion | failure, RL) > P(assertion | failure, DPO)
using one-sided Fisher's exact test on 2x2 contingency table.
"""

import json
import os
from typing import Dict, List, Tuple

import numpy as np
from scipy.stats import fisher_exact

from config import HM1Config


def build_assertion_contingency(
    rl_counts: Dict[str, int],
    dpo_counts: Dict[str, int],
) -> np.ndarray:
    """Build 2x2 contingency table: [RL, DPO] x [assertion, non-assertion].

    Args:
        rl_counts: Dict with keys 'assertion', 'syntax', 'runtime', 'other'
        dpo_counts: Dict with keys 'assertion', 'syntax', 'runtime', 'other'

    Returns:
        2x2 numpy array: [[rl_assert, rl_non_assert], [dpo_assert, dpo_non_assert]]
    """
    # RL row
    rl_assertion = rl_counts.get("assertion", 0)
    rl_non_assertion = (
        rl_counts.get("syntax", 0)
        + rl_counts.get("runtime", 0)
        + rl_counts.get("other", 0)
    )

    # DPO row
    dpo_assertion = dpo_counts.get("assertion", 0)
    dpo_non_assertion = (
        dpo_counts.get("syntax", 0)
        + dpo_counts.get("runtime", 0)
        + dpo_counts.get("other", 0)
    )

    return np.array([
        [rl_assertion, rl_non_assertion],
        [dpo_assertion, dpo_non_assertion]
    ])


def run_fisher_exact_test(
    contingency: np.ndarray,
    alternative: str = "greater",
) -> Tuple[float, float]:
    """One-sided Fisher's exact test: P(assertion|fail,RL) > P(assertion|fail,DPO).

    Args:
        contingency: 2x2 numpy array [[rl_assert, rl_non], [dpo_assert, dpo_non]]
        alternative: 'greater' for one-sided test (RL > DPO)

    Returns:
        Tuple of (odds_ratio, p_value)
    """
    odds_ratio, p_value = fisher_exact(contingency, alternative=alternative)
    return float(odds_ratio), float(p_value)


def compute_assertion_proportions(
    rl_counts: Dict[str, int],
    dpo_counts: Dict[str, int],
) -> Dict[str, float]:
    """Compute P(assertion | failure) for each model.

    Args:
        rl_counts: Error counts for RL model
        dpo_counts: Error counts for DPO model

    Returns:
        Dict with keys: rl_assertion_prop, dpo_assertion_prop,
                        rl_assertion_count, dpo_assertion_count,
                        rl_total_failures, dpo_total_failures
    """
    # Total failures (excluding 'pass')
    rl_total = (
        rl_counts.get("syntax", 0)
        + rl_counts.get("runtime", 0)
        + rl_counts.get("assertion", 0)
        + rl_counts.get("other", 0)
    )
    dpo_total = (
        dpo_counts.get("syntax", 0)
        + dpo_counts.get("runtime", 0)
        + dpo_counts.get("assertion", 0)
        + dpo_counts.get("other", 0)
    )

    rl_assertion = rl_counts.get("assertion", 0)
    dpo_assertion = dpo_counts.get("assertion", 0)

    return {
        "rl_assertion_prop": rl_assertion / rl_total if rl_total > 0 else 0.0,
        "dpo_assertion_prop": dpo_assertion / dpo_total if dpo_total > 0 else 0.0,
        "rl_assertion_count": rl_assertion,
        "dpo_assertion_count": dpo_assertion,
        "rl_total_failures": rl_total,
        "dpo_total_failures": dpo_total,
    }


def run_analysis(
    rl_results: List[dict],
    dpo_results: List[dict],
    config: HM1Config,
) -> Dict:
    """Full H-M1 analysis pipeline.

    Args:
        rl_results: RL execution results with 'error_trace' key
        dpo_results: DPO execution results with 'error_trace' key
        config: H-M1 configuration

    Returns:
        Complete metrics dict with Fisher's exact test results
    """
    from data_loader import extract_error_counts

    # Extract error counts using H-E1 classify_error
    rl_counts = extract_error_counts(rl_results, config.h_e1_code_dir)
    dpo_counts = extract_error_counts(dpo_results, config.h_e1_code_dir)

    print(f"RL error counts: {rl_counts}")
    print(f"DPO error counts: {dpo_counts}")

    # Compute assertion proportions
    props = compute_assertion_proportions(rl_counts, dpo_counts)

    # Build 2x2 contingency table
    contingency = build_assertion_contingency(rl_counts, dpo_counts)

    print(f"2x2 Contingency table (assertion vs non-assertion):")
    print(f"         assertion  non-assertion")
    print(f"RL:      {contingency[0][0]:9d}  {contingency[0][1]:13d}")
    print(f"DPO:     {contingency[1][0]:9d}  {contingency[1][1]:13d}")

    # Run Fisher's exact test (one-sided)
    odds_ratio, p_value = run_fisher_exact_test(contingency, config.alternative)

    # Check gate conditions
    direction_matches = props["rl_assertion_prop"] > props["dpo_assertion_prop"]
    gate_pass = (p_value < config.fisher_p_threshold) and direction_matches

    # Build mechanism log message
    mechanism_log = (
        f"H-M1: RL assertion proportion = {props['rl_assertion_prop']*100:.2f}%, "
        f"DPO assertion proportion = {props['dpo_assertion_prop']*100:.2f}%"
    )

    metrics = {
        # Assertion counts
        "rl_assertion_count": props["rl_assertion_count"],
        "rl_total_failures": props["rl_total_failures"],
        "rl_assertion_prop": props["rl_assertion_prop"],
        "dpo_assertion_count": props["dpo_assertion_count"],
        "dpo_total_failures": props["dpo_total_failures"],
        "dpo_assertion_prop": props["dpo_assertion_prop"],
        # Fisher's exact test
        "odds_ratio": odds_ratio,
        "p_value": p_value,
        "alternative": config.alternative,
        # Gate results
        "gate_pass": gate_pass,
        "direction_matches": direction_matches,
        "fisher_p_threshold": config.fisher_p_threshold,
        # Contingency table
        "contingency_table": contingency.tolist(),
        # Mechanism log
        "mechanism_log": mechanism_log,
        # Full error counts for visualization
        "rl_counts": rl_counts,
        "dpo_counts": dpo_counts,
    }

    # Save outputs
    os.makedirs(config.output_dir, exist_ok=True)

    # Save metrics.json
    metrics_path = os.path.join(config.output_dir, "metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved metrics to {metrics_path}")

    # Save experiment_results.json
    experiment_results = {
        "hypothesis_id": "h-m1",
        "experiment_name": "Zero-Reward Basin Mechanism Analysis",
        "gate_type": "MUST_WORK",
        "gate_pass": gate_pass,
        "metrics": metrics,
        "mechanism_verified": gate_pass,
    }
    results_path = os.path.join(config.output_dir, "experiment_results.json")
    with open(results_path, "w") as f:
        json.dump(experiment_results, f, indent=2)
    print(f"Saved experiment results to {results_path}")

    # Save contingency table CSV
    csv_path = os.path.join(config.output_dir, "contingency_table.csv")
    with open(csv_path, "w") as f:
        f.write("model,assertion,non_assertion\n")
        f.write(f"rl,{contingency[0][0]},{contingency[0][1]}\n")
        f.write(f"dpo,{contingency[1][0]},{contingency[1][1]}\n")
    print(f"Saved contingency table to {csv_path}")

    return metrics
