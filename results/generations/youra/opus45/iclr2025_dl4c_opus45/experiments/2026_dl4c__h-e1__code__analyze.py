"""Error classification and statistical analysis using ICSE 2025 taxonomy."""

import json
import os
from collections import Counter
from typing import Dict, List, Optional, Tuple

import numpy as np
from scipy.stats import chi2_contingency

from config import ExperimentConfig

# ICSE 2025 Error Taxonomy
ERROR_CATEGORIES = ["syntax", "runtime", "assertion"]

SYNTAX_ERRORS = ["syntaxerror", "indentationerror"]
RUNTIME_ERRORS = [
    "typeerror", "nameerror", "attributeerror",
    "indexerror", "keyerror", "valueerror",
    "zerodivisionerror", "recursionerror", "timeout"
]
ASSERTION_ERRORS = ["assertionerror", "expected"]


def classify_error(error_trace: Optional[str]) -> str:
    """Classify error_trace using ICSE 2025 taxonomy.

    Args:
        error_trace: Error string or None for pass

    Returns:
        One of: "pass", "syntax", "runtime", "assertion", "other"
    """
    if error_trace is None:
        return "pass"

    error_lower = error_trace.lower()

    # Syntax errors (parse-time failures)
    for err in SYNTAX_ERRORS:
        if err in error_lower:
            return "syntax"

    # Assertion errors (code runs but wrong output)
    for err in ASSERTION_ERRORS:
        if err in error_lower:
            return "assertion"

    # Runtime errors (execution-time failures before assertion)
    for err in RUNTIME_ERRORS:
        if err in error_lower:
            return "runtime"

    return "other"


def build_contingency_table(
    rl_results: List[dict],
    dpo_results: List[dict],
) -> np.ndarray:
    """Build 2x3 contingency table from failed samples only (exclude pass).

    Args:
        rl_results: Execution results for RL model
        dpo_results: Execution results for DPO model

    Returns:
        2x3 numpy array: rows=[rl, dpo], cols=[syntax, runtime, assertion]
    """
    def count_errors(results: List[dict]) -> List[int]:
        classifications = [classify_error(r["error_trace"]) for r in results]
        # Only count failures, not passes
        failures = [c for c in classifications if c != "pass"]
        counts = Counter(failures)
        return [counts.get(cat, 0) for cat in ERROR_CATEGORIES]

    rl_counts = count_errors(rl_results)
    dpo_counts = count_errors(dpo_results)

    return np.array([rl_counts, dpo_counts])


def chi_square_test(contingency: np.ndarray) -> Tuple[float, float, float, int]:
    """Run scipy.stats.chi2_contingency; compute Cramér's V.

    Args:
        contingency: 2x3 array

    Returns:
        (chi2, p_value, cramers_v, dof)
        cramers_v = sqrt(chi2 / (n * (min(r, c) - 1)))
    """
    chi2, p_value, dof, expected = chi2_contingency(contingency)

    # Compute Cramér's V
    n = contingency.sum()
    min_dim = min(contingency.shape) - 1  # min(2, 3) - 1 = 1
    cramers_v = np.sqrt(chi2 / (n * min_dim)) if n > 0 and min_dim > 0 else 0.0

    return chi2, p_value, cramers_v, dof


def compute_proportions(results: List[dict]) -> Dict[str, float]:
    """Compute P(type | failure) for each ERROR_CATEGORY.

    Args:
        results: Execution results

    Returns:
        Dict mapping error category to proportion among failures
    """
    classifications = [classify_error(r["error_trace"]) for r in results]
    failures = [c for c in classifications if c != "pass"]

    if not failures:
        return {cat: 0.0 for cat in ERROR_CATEGORIES}

    counts = Counter(failures)
    total = len(failures)

    return {cat: counts.get(cat, 0) / total for cat in ERROR_CATEGORIES}


def check_effect_direction(
    rl_results: List[dict],
    dpo_results: List[dict],
) -> Tuple[float, float, bool]:
    """Check if P(syntax+runtime | failure, RL) < P(syntax+runtime | failure, DPO).

    The hypothesis predicts that RL-aligned models have fewer syntax+runtime errors
    (more assertion errors) because RL training optimizes for execution success.

    Args:
        rl_results: Execution results for RL model
        dpo_results: Execution results for DPO model

    Returns:
        (rl_prop, dpo_prop, direction_matches)
        direction_matches = rl_prop < dpo_prop
    """
    rl_props = compute_proportions(rl_results)
    dpo_props = compute_proportions(dpo_results)

    # Sum syntax + runtime proportions
    rl_syntax_runtime = rl_props["syntax"] + rl_props["runtime"]
    dpo_syntax_runtime = dpo_props["syntax"] + dpo_props["runtime"]

    direction_matches = rl_syntax_runtime < dpo_syntax_runtime

    return rl_syntax_runtime, dpo_syntax_runtime, direction_matches


def run_analysis(
    rl_results: List[dict],
    dpo_results: List[dict],
    config: ExperimentConfig,
) -> Dict:
    """Full analysis pipeline. Saves outputs/metrics.json.

    Args:
        rl_results: Execution results for RL model
        dpo_results: Execution results for DPO model
        config: Experiment configuration

    Returns:
        Dict with keys: chi2, p_value, cramers_v, dof, direction_matches,
        rl_proportions, dpo_proportions, gate_pass
        gate_pass = (p_value < chi2_p_threshold) and (cramers_v > cramers_v_threshold)
    """
    # Build contingency table
    contingency = build_contingency_table(rl_results, dpo_results)

    # Run chi-square test
    chi2, p_value, cramers_v, dof = chi_square_test(contingency)

    # Compute proportions
    rl_proportions = compute_proportions(rl_results)
    dpo_proportions = compute_proportions(dpo_results)

    # Check direction
    rl_sr_prop, dpo_sr_prop, direction_matches = check_effect_direction(rl_results, dpo_results)

    # Count failures
    rl_failures = sum(1 for r in rl_results if r["status"] == "fail")
    dpo_failures = sum(1 for r in dpo_results if r["status"] == "fail")

    # Gate check
    gate_pass = (p_value < config.chi2_p_threshold) and (cramers_v > config.cramers_v_threshold)

    metrics = {
        "chi2": float(chi2),
        "p_value": float(p_value),
        "cramers_v": float(cramers_v),
        "dof": int(dof),
        "direction_matches": bool(direction_matches),
        "rl_syntax_runtime_prop": float(rl_sr_prop),
        "dpo_syntax_runtime_prop": float(dpo_sr_prop),
        "rl_proportions": rl_proportions,
        "dpo_proportions": dpo_proportions,
        "rl_failures": rl_failures,
        "dpo_failures": dpo_failures,
        "total_samples": len(rl_results) + len(dpo_results),
        "contingency_table": contingency.tolist(),
        "thresholds": {
            "chi2_p_threshold": config.chi2_p_threshold,
            "cramers_v_threshold": config.cramers_v_threshold
        },
        "gate_pass": bool(gate_pass)
    }

    # Save metrics
    output_path = os.path.join(config.output_dir, "metrics.json")
    os.makedirs(config.output_dir, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved metrics to {output_path}")

    # Save contingency table as CSV
    csv_path = os.path.join(config.output_dir, "contingency_table.csv")
    with open(csv_path, "w") as f:
        f.write("model," + ",".join(ERROR_CATEGORIES) + "\n")
        f.write("rl," + ",".join(str(x) for x in contingency[0]) + "\n")
        f.write("dpo," + ",".join(str(x) for x in contingency[1]) + "\n")
    print(f"Saved contingency table to {csv_path}")

    return metrics
