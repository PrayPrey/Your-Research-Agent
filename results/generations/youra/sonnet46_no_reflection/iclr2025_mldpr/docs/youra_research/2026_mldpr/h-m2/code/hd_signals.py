"""H-M2: H_d Signal Computation — CV/NLP/Tabular domain-specific degradation signals.

Since PWC domain mapping covers only ~0.5% of benchmarks (most are 'other'),
we compute ALL three signal types for ALL benchmarks as independent degradation proxies:
- hd_cv: rolling std of score_var_top10 (volatility/robustness gap proxy)
- hd_nlp: normalized deviation from early baseline (contamination/drift proxy)
- hd_tabular: block-bootstrapped Kendall tau (rank stability proxy)

This enables cross-domain analysis on the full panel regardless of PWC task labels.
"""
import numpy as np
import pandas as pd
import scipy.stats

DOMAIN_THRESHOLDS: dict = {"cv": 0.5, "nlp": 0.3, "tabular": 0.90}


def compute_robustness_gap_cv(
    panel_df: pd.DataFrame,
    benchmark_id: str,
    rolling_quarters: int = 4,
) -> pd.DataFrame:
    """Rolling std of score_var_top10 as CV robustness gap proxy."""
    bm = panel_df[panel_df["benchmark_id"] == benchmark_id].sort_values("quarter").copy()
    if len(bm) < 2:
        bm["hd_cv"] = np.nan
        return bm[["quarter", "hd_cv"]]
    bm["hd_cv"] = bm["score_var_top10"].rolling(
        window=min(rolling_quarters, len(bm)), min_periods=2
    ).std()
    return bm[["quarter", "hd_cv"]].reset_index(drop=True)


def compute_contamination_nlp(
    panel_df: pd.DataFrame,
    benchmark_id: str,
) -> pd.DataFrame:
    """Normalized absolute deviation from early baseline as contamination proxy."""
    bm = panel_df[panel_df["benchmark_id"] == benchmark_id].sort_values("quarter").copy()
    if len(bm) == 0:
        bm["hd_nlp"] = np.nan
        return bm[["quarter", "hd_nlp"]]
    # Use first 2 quarters as baseline
    baseline = bm["score_var_top10"].iloc[:min(2, len(bm))].mean()
    if baseline == 0 or np.isnan(baseline):
        baseline = bm["score_var_top10"].median()
    if baseline == 0 or np.isnan(baseline):
        bm["hd_nlp"] = np.nan
    else:
        bm["hd_nlp"] = (bm["score_var_top10"] - baseline).abs() / (abs(baseline) + 1e-9)
    return bm[["quarter", "hd_nlp"]].reset_index(drop=True)


def compute_kendall_tau_tabular(
    panel_df: pd.DataFrame,
    benchmark_id: str,
    bootstrap_iters: int = 100,
    seed: int = 42,
) -> pd.DataFrame:
    """Block-bootstrapped Kendall tau rank correlation (rank stability proxy)."""
    bm = panel_df[panel_df["benchmark_id"] == benchmark_id].sort_values("quarter").copy()
    if len(bm) < 4:
        bm["hd_tabular"] = np.nan
        return bm[["quarter", "hd_tabular"]].reset_index(drop=True)

    rng = np.random.default_rng(seed)
    scores = bm["score_var_top10"].values
    n = len(scores)
    taus = []
    for _ in range(bootstrap_iters):
        idx = rng.choice(n, size=n, replace=True)
        sample = scores[idx]
        if len(np.unique(sample)) < 2:
            continue
        tau, _ = scipy.stats.kendalltau(np.arange(n), sample)
        if not np.isnan(tau):
            taus.append(tau)

    mean_tau = float(np.mean(taus)) if taus else np.nan
    bm["hd_tabular"] = mean_tau
    return bm[["quarter", "hd_tabular"]].reset_index(drop=True)


def compute_all_hd_signals(
    panel_df: pd.DataFrame,
    bootstrap_iters: int = 100,
    seed: int = 42,
) -> pd.DataFrame:
    """Compute ALL three H_d signals for ALL benchmarks.

    Since PWC domain labels cover <1% of benchmarks, we compute all signal
    types universally. Each benchmark gets hd_cv, hd_nlp, and hd_tabular.
    """
    all_results = []
    bm_ids = panel_df["benchmark_id"].unique()
    total = len(bm_ids)

    for i, bm_id in enumerate(bm_ids):
        bm_data = panel_df[panel_df["benchmark_id"] == bm_id].copy()

        # Compute all three signals for every benchmark
        cv_sig = compute_robustness_gap_cv(panel_df, bm_id)
        nlp_sig = compute_contamination_nlp(panel_df, bm_id)
        tab_sig = compute_kendall_tau_tabular(panel_df, bm_id,
                                               bootstrap_iters=bootstrap_iters, seed=seed)

        # Merge signals into benchmark data
        bm_data = bm_data.merge(cv_sig, on="quarter", how="left", suffixes=("", "_cv_new"))
        bm_data = bm_data.merge(nlp_sig, on="quarter", how="left", suffixes=("", "_nlp_new"))
        bm_data = bm_data.merge(tab_sig, on="quarter", how="left", suffixes=("", "_tab_new"))

        # Resolve any suffix conflicts
        for col, new_col in [("hd_cv", "hd_cv_cv_new"), ("hd_nlp", "hd_nlp_nlp_new"),
                              ("hd_tabular", "hd_tabular_tab_new")]:
            if new_col in bm_data.columns:
                bm_data[col] = bm_data[new_col]
                bm_data.drop(columns=[new_col], inplace=True)

        all_results.append(bm_data)

        if (i + 1) % 100 == 0:
            print(f"    H_d signals: {i+1}/{total} benchmarks processed")

    if not all_results:
        panel_df = panel_df.copy()
        for col in ["hd_cv", "hd_nlp", "hd_tabular"]:
            panel_df[col] = np.nan
        return panel_df

    merged = pd.concat(all_results, ignore_index=True)
    for col in ["hd_cv", "hd_nlp", "hd_tabular"]:
        if col not in merged.columns:
            merged[col] = np.nan
    print(f"    H_d signals complete: {total} benchmarks")
    return merged
