"""H-M1: Spearman Baseline — co-occurrence correlation test."""
import pandas as pd
import numpy as np
from scipy.stats import spearmanr


def compute_spearman_baseline(panel_df: pd.DataFrame) -> dict:
    """Spearman rho between cumulative_count and compression_event.
    Drops rows with NaN in either column.
    Returns: {'rho': float, 'p_value': float, 'n_obs': int}
    """
    required = ["cumulative_count", "compression_event"]
    for col in required:
        if col not in panel_df.columns:
            return {"rho": float("nan"), "p_value": float("nan"), "n_obs": 0}

    valid = panel_df[required].dropna()
    n_obs = len(valid)

    if n_obs < 3:
        return {"rho": float("nan"), "p_value": float("nan"), "n_obs": n_obs}

    rho, p_value = spearmanr(valid["cumulative_count"], valid["compression_event"])
    return {
        "rho": float(rho) if not np.isnan(rho) else float("nan"),
        "p_value": float(p_value) if not np.isnan(p_value) else float("nan"),
        "n_obs": n_obs,
    }
