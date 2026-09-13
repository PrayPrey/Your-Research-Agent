"""Efficiency frontier analysis and statistical testing."""

import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from typing import Dict, Tuple, List
import json
import os

def compute_efficiency(pass_at_1: float, sft_baseline: float, bits: float) -> float:
    """Compute feedback efficiency in pp/bit.

    Args:
        pass_at_1: Pass@1 rate for condition
        sft_baseline: SFT baseline pass@1
        bits: Information content in bits

    Returns:
        Efficiency in percentage points per bit
    """
    return (pass_at_1 - sft_baseline) * 100.0 / bits

def pairwise_ttests(efficiencies: Dict[str, List[float]]) -> Dict[str, float]:
    """Pairwise t-tests with Bonferroni correction.

    Args:
        efficiencies: {"binary": [samples], "error_type": [samples], "error_trace": [samples]}

    Returns:
        {comparison: p_value}
    """
    comparisons = [
        ("binary", "error_type"),
        ("error_type", "error_trace"),
        ("binary", "error_trace")
    ]

    results = {}
    for cond_a, cond_b in comparisons:
        t_stat, p_value = stats.ttest_ind(efficiencies[cond_a], efficiencies[cond_b], alternative='greater')
        results[f"{cond_a}_vs_{cond_b}"] = p_value

    return results

def bootstrap_ci(pass_at_1_samples: List[float], sft_baseline: float, bits: float, n_bootstrap: int = 1000) -> Tuple[float, float]:
    """Bootstrap 95% confidence interval for efficiency.

    Args:
        pass_at_1_samples: Bootstrap samples of pass@1 rates
        sft_baseline: SFT baseline pass@1
        bits: Information content
        n_bootstrap: Number of bootstrap iterations

    Returns:
        (lower, upper) confidence bounds
    """
    efficiencies = []
    for _ in range(n_bootstrap):
        sample = np.random.choice(pass_at_1_samples, size=len(pass_at_1_samples), replace=True)
        eff = compute_efficiency(np.mean(sample), sft_baseline, bits)
        efficiencies.append(eff)

    lower = np.percentile(efficiencies, 2.5)
    upper = np.percentile(efficiencies, 97.5)
    return (lower, upper)

def plot_efficiency_frontier(results: Dict[str, Dict], output_path: str):
    """Plot efficiency frontier with error bars.

    Args:
        results: {"binary": {"eff": float, "ci": (lower, upper)}, ...}
        output_path: Path to save figure
    """
    conditions = ["binary", "error_type", "error_trace"]
    labels = ["Binary", "Error-Type", "Error+Trace"]
    efficiencies = [results[c]["eff"] for c in conditions]
    ci_lowers = [results[c]["eff"] - results[c]["ci"][0] for c in conditions]
    ci_uppers = [results[c]["ci"][1] - results[c]["eff"] for c in conditions]

    fig, ax = plt.subplots(figsize=(8, 6))
    x = np.arange(len(labels))
    ax.bar(x, efficiencies, yerr=[ci_lowers, ci_uppers], capsize=5, color=['blue', 'orange', 'green'], alpha=0.7)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Efficiency (pp/bit)")
    ax.set_xlabel("Feedback Granularity")
    ax.axhline(7.0, color='red', linestyle='--', label='Binary target (7 pp/bit)')
    ax.axhline(5.0, color='orange', linestyle='--', label='Error-Type target (5 pp/bit)')
    ax.axhline(2.5, color='green', linestyle='--', label='Error+Trace target (2.5 pp/bit)')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close()

def gate_verdict(
    results: Dict[str, float],
    p_values: Dict[str, float],
    bits: Dict[str, float],
    sft_baseline: float,
    alpha: float = 0.0167
) -> Tuple[bool, str]:
    """Determine MUST_WORK gate pass/fail.

    Args:
        results: {"binary": pass@1, "error_type": pass@1, "error_trace": pass@1}
        p_values: {"binary_vs_error_type": p, "error_type_vs_error_trace": p, "binary_vs_error_trace": p}
        bits: {"binary": 1.0, "error_type": 2.32, "error_trace": 5.64}
        sft_baseline: SFT pass@1
        alpha: Bonferroni corrected alpha

    Returns:
        (pass_bool, reason_str)
    """
    # Compute efficiencies
    eff_binary = compute_efficiency(results["binary"], sft_baseline, bits["binary"])
    eff_error_type = compute_efficiency(results["error_type"], sft_baseline, bits["error_type"])
    eff_error_trace = compute_efficiency(results["error_trace"], sft_baseline, bits["error_trace"])

    # Check monotonic decrease
    monotonic = (eff_binary > eff_error_type > eff_error_trace)

    # Check target ranges
    in_range_binary = eff_binary >= 7.0
    in_range_error_type = 4.0 <= eff_error_type <= 6.0
    in_range_error_trace = 2.0 <= eff_error_trace <= 3.0

    # Check statistical significance
    sig_binary_vs_error = p_values["binary_vs_error_type"] < alpha
    sig_error_vs_trace = p_values["error_type_vs_error_trace"] < alpha
    sig_binary_vs_trace = p_values["binary_vs_error_trace"] < alpha

    all_significant = sig_binary_vs_error and sig_error_vs_trace and sig_binary_vs_trace

    # Gate logic
    if monotonic and in_range_binary and in_range_error_type and in_range_error_trace and all_significant:
        return (True, f"PASS: Monotonic decrease confirmed (Binary {eff_binary:.2f} > Error-Type {eff_error_type:.2f} > Error+Trace {eff_error_trace:.2f} pp/bit), all conditions met")
    else:
        reasons = []
        if not monotonic:
            reasons.append(f"Monotonic decrease violated: Binary {eff_binary:.2f}, Error-Type {eff_error_type:.2f}, Error+Trace {eff_error_trace:.2f} pp/bit")
        if not in_range_binary:
            reasons.append(f"Binary efficiency {eff_binary:.2f} < 7.0 pp/bit")
        if not in_range_error_type:
            reasons.append(f"Error-Type efficiency {eff_error_type:.2f} not in [4.0, 6.0] pp/bit")
        if not in_range_error_trace:
            reasons.append(f"Error+Trace efficiency {eff_error_trace:.2f} not in [2.0, 3.0] pp/bit")
        if not all_significant:
            reasons.append(f"Statistical tests failed (alpha={alpha}): {p_values}")
        return (False, "FAIL: " + "; ".join(reasons))

def generate_validation_report(
    results: Dict[str, float],
    efficiencies: Dict[str, float],
    p_values: Dict[str, float],
    gate_status: Tuple[bool, str],
    output_path: str
):
    """Generate efficiency metrics JSON + gate verdict.

    Args:
        results: {"sft": pass@1, "binary": pass@1, ...}
        efficiencies: {"binary": eff, "error_type": eff, ...}
        p_values: {"binary_vs_error_type": p, ...}
        gate_status: (pass_bool, reason)
        output_path: Path to save report
    """
    report = {
        "pass_at_1": results,
        "efficiencies": efficiencies,
        "p_values": p_values,
        "gate": {
            "status": "PASS" if gate_status[0] else "FAIL",
            "reason": gate_status[1]
        }
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
