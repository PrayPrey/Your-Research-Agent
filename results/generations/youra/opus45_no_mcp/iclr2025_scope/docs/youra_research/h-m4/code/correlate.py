"""Correlation analysis for H-M4: Spearman correlation + gate check"""

from scipy.stats import spearmanr
import numpy as np

from config import GATE_THRESHOLD


def compute_spearman_gate(densities: list, accuracy_deltas: list):
    """
    Spearman correlation between retrieval density and accuracy delta.
    Returns {'rho': float, 'p_value': float, 'gate_pass': bool}
    """
    if len(densities) < 2:
        return {
            "rho": 0.0,
            "p_value": 1.0,
            "gate_pass": False,
        }

    rho, p_value = spearmanr(densities, accuracy_deltas)

    if np.isnan(rho):
        rho = 0.0
    if np.isnan(p_value):
        p_value = 1.0

    gate_pass = abs(rho) >= GATE_THRESHOLD["min_spearman_rho"] and p_value < GATE_THRESHOLD["max_p_value"]

    return {
        "rho": float(rho),
        "p_value": float(p_value),
        "gate_pass": gate_pass,
    }


def check_monotonicity(values: list):
    """Check if values are monotonically increasing or decreasing."""
    if len(values) < 2:
        return True

    increasing = all(values[i] <= values[i+1] for i in range(len(values)-1))
    decreasing = all(values[i] >= values[i+1] for i in range(len(values)-1))

    return increasing or decreasing


def analyze_correlation(results_table: dict):
    """
    Full correlation analysis.
    Returns correlation metrics + gate result.
    """
    sorted_tasks = sorted(results_table.keys(), key=lambda t: results_table[t]["density"])

    densities = [results_table[t]["density"] for t in sorted_tasks]
    accuracy_deltas = [results_table[t]["delta"]["accuracy_delta"] for t in sorted_tasks]
    sharpness_deltas = [results_table[t]["delta"]["sharpness_delta"] for t in sorted_tasks]
    rank_deltas = [results_table[t]["delta"]["rank_delta"] for t in sorted_tasks]

    primary = compute_spearman_gate(densities, accuracy_deltas)
    primary["is_monotonic"] = check_monotonicity(accuracy_deltas)

    sharpness_corr = spearmanr(densities, sharpness_deltas) if len(densities) >= 2 else (0.0, 1.0)
    rank_corr = spearmanr(densities, rank_deltas) if len(densities) >= 2 else (0.0, 1.0)

    return {
        "primary": primary,
        "ablations": {
            "sharpness_delta": {
                "rho": float(sharpness_corr[0]) if not np.isnan(sharpness_corr[0]) else 0.0,
                "p_value": float(sharpness_corr[1]) if not np.isnan(sharpness_corr[1]) else 1.0,
            },
            "rank_delta": {
                "rho": float(rank_corr[0]) if not np.isnan(rank_corr[0]) else 0.0,
                "p_value": float(rank_corr[1]) if not np.isnan(rank_corr[1]) else 1.0,
            },
        },
        "data": {
            "tasks": sorted_tasks,
            "densities": densities,
            "accuracy_deltas": accuracy_deltas,
            "sharpness_deltas": sharpness_deltas,
            "rank_deltas": rank_deltas,
        }
    }
