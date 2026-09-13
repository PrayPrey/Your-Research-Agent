"""H-M2: Collapse Event Detection — expanding Kendall tau + consecutive flag."""
import numpy as np
import pandas as pd
import scipy.stats


def detect_collapse_events(
    panel_df: pd.DataFrame,
    tau_threshold: float = 0.90,
    min_consecutive: int = 2,
) -> pd.DataFrame:
    """Identify collapse: expanding Kendall tau > tau_threshold for >= 2 consecutive quarters.
    Returns: DataFrame[benchmark_id, collapse_quarter]
    """
    collapse_records = []
    for bm_id, bm_data in panel_df.groupby("benchmark_id"):
        bm_sorted = bm_data.sort_values("quarter").reset_index(drop=True)
        scores = bm_sorted["score_var_top10"].values
        n = len(scores)
        if n < 4:
            continue

        tau_vals = []
        for i in range(n):
            window = scores[: i + 1]
            if len(window) < 3:
                tau_vals.append(0.0)
            else:
                tau, _ = scipy.stats.kendalltau(np.arange(len(window)), window)
                tau_vals.append(float(tau) if not np.isnan(tau) else 0.0)

        tau_series = pd.Series(tau_vals)
        collapse_flag = (tau_series > tau_threshold).astype(float)
        consecutive = collapse_flag.rolling(min_consecutive).min()

        if (consecutive == 1.0).any():
            first_idx = consecutive[consecutive == 1.0].index[0]
            collapse_q = bm_sorted.iloc[first_idx]["quarter"]
            collapse_records.append({"benchmark_id": bm_id, "collapse_quarter": collapse_q})

    return pd.DataFrame(collapse_records) if collapse_records else pd.DataFrame(columns=["benchmark_id", "collapse_quarter"])


def apply_r1_mitigation(
    panel_df: pd.DataFrame,
    collapse_df: pd.DataFrame,
    min_events: int = 20,
    lower_tau: float = 0.85,
) -> tuple:
    """If len(collapse_df) < min_events, re-detect with lower_tau threshold.
    Returns: (collapse_df, tau_used)
    """
    if len(collapse_df) >= min_events:
        return collapse_df, 0.90

    print(f"⚠ R1 mitigation: only {len(collapse_df)} events (< {min_events}), retrying with tau={lower_tau}")
    new_collapse_df = detect_collapse_events(panel_df, tau_threshold=lower_tau, min_consecutive=2)
    print(f"  → After mitigation: {len(new_collapse_df)} collapse events")
    return new_collapse_df, lower_tau
