"""Statistical analysis for BCS distribution."""

import numpy as np
from scipy import stats
from config import BCS_SD_TARGET, N_TARGET


def analyze_bcs_distribution(bcs_values: list) -> dict:
    """Compute distribution statistics, excluding NaN."""
    clean = [b for b in bcs_values if not np.isnan(b)]
    if not clean:
        return {"n": 0, "mean": 0, "std": 0, "gate_pass": False}

    return {
        "n": len(clean),
        "mean": float(np.mean(clean)),
        "median": float(np.median(clean)),
        "std": float(np.std(clean)),
        "min": float(np.min(clean)),
        "max": float(np.max(clean)),
        "skewness": float(stats.skew(clean)),
        "gate_pass": check_gate({"std": np.std(clean), "n": len(clean)})
    }


def check_gate(stats_dict: dict, sd_target: float = BCS_SD_TARGET, n_target: int = N_TARGET) -> bool:
    """Check if gate conditions are satisfied."""
    return stats_dict.get("std", 0) > sd_target and stats_dict.get("n", 0) > n_target
