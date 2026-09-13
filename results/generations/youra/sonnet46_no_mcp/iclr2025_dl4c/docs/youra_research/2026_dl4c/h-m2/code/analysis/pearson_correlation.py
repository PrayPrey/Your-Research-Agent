import json
import numpy as np
from scipy import stats
from typing import Optional

from .compute_gains import build_pooled_observations, CONDITIONS
from .compute_entropy import add_entropy_column, compute_early_mean_entropy


def pearson_with_ci(x: np.ndarray, y: np.ndarray) -> dict:
    """Pearson r with 95% CI via Fisher z-transformation."""
    n = len(x)
    r, p_twotailed = stats.pearsonr(x, y)
    p_onetailed = float(p_twotailed) / 2.0

    z = np.arctanh(float(r))
    se = 1.0 / np.sqrt(n - 3)
    z_crit = 1.96
    ci_low = float(np.tanh(z - z_crit * se))
    ci_high = float(np.tanh(z + z_crit * se))

    return {
        "r": float(r),
        "p_twotailed": float(p_twotailed),
        "p_onetailed": p_onetailed,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "n": int(n),
    }


def per_condition_correlations(data: dict) -> dict:
    """Pearson r per condition. Returns {cond: {r, p_onetailed, n}}."""
    result = {}
    for cond in CONDITIONS:
        density_df = data[cond]["density"].sort_values("step").reset_index(drop=True)
        pass1_df = data[cond]["pass1"].sort_values("step").reset_index(drop=True)

        n_ckpts = min(len(density_df), len(pass1_df))
        n_intervals = min(n_ckpts - 1, 9)

        if n_intervals < 3:
            result[cond] = {"r": float("nan"), "p_onetailed": float("nan"), "n": n_intervals}
            continue

        densities = density_df["reward_density"].values[:n_intervals]
        gains = np.diff(pass1_df["pass1"].values[:n_intervals + 1])

        try:
            r, p_two = stats.pearsonr(densities, gains)
            result[cond] = {
                "r": float(r),
                "p_onetailed": float(p_two) / 2.0,
                "n": n_intervals,
            }
        except Exception as e:
            result[cond] = {"r": float("nan"), "p_onetailed": float("nan"), "n": n_intervals, "error": str(e)}

    return result


def wilcoxon_entropy_test(
    entropy_curriculum_early: np.ndarray,
    entropy_uniform_early: np.ndarray,
) -> dict:
    """One-tailed Wilcoxon signed-rank test (curriculum > uniform)."""
    direction_correct = bool(np.mean(entropy_curriculum_early) > np.mean(entropy_uniform_early))

    if len(entropy_curriculum_early) < 2:
        return {"statistic": float("nan"), "p_value": float("nan"), "direction_correct": direction_correct}

    try:
        stat, p_two = stats.wilcoxon(entropy_curriculum_early, entropy_uniform_early)
        p_one = float(p_two) / 2.0 if direction_correct else 1.0 - float(p_two) / 2.0
        return {"statistic": float(stat), "p_value": p_one, "direction_correct": direction_correct}
    except Exception as e:
        return {"statistic": float("nan"), "p_value": float("nan"), "direction_correct": direction_correct, "error": str(e)}


def evaluate_gate(pearson_result: dict) -> bool:
    """Returns True if r > 0.5 AND p_onetailed < 0.05."""
    return pearson_result["r"] > 0.5 and pearson_result["p_onetailed"] < 0.05


def save_results(
    pooled_pearson: dict,
    entropy_comparison: dict,
    per_condition_r: dict,
    wilcoxon_result: dict,
    output_path: str,
) -> None:
    """Write results_summary.json with all gate metrics."""
    gate_passed = evaluate_gate(pooled_pearson)
    summary = {
        "gate_passed": gate_passed,
        "gate_type": "SHOULD_WORK",
        "pearson_r": pooled_pearson["r"],
        "p_value_twotailed": pooled_pearson["p_twotailed"],
        "p_value_onetailed": pooled_pearson["p_onetailed"],
        "ci_low": pooled_pearson["ci_low"],
        "ci_high": pooled_pearson["ci_high"],
        "n_pooled_observations": pooled_pearson["n"],
        "entropy_comparison": entropy_comparison,
        "per_condition_correlations": per_condition_r,
        "wilcoxon_entropy_test": wilcoxon_result,
    }
    with open(output_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Results saved to {output_path}")
