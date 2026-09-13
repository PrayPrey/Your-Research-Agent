"""H-M2: Statistical Tests — Mann-Whitney U + AUC comparison."""
import numpy as np
import pandas as pd
import scipy.stats
from sklearn.metrics import roc_auc_score


def run_mann_whitney_test(
    panel_df: pd.DataFrame,
    domain: str,
    compressed_ids,
) -> dict:
    """Mann-Whitney U: H_d magnitude higher in compressed vs. non-compressed benchmarks.
    Returns: {mw_stat, mw_p_value, domain, n_compressed, n_non_compressed}
    """
    hd_col = f"hd_{domain}"
    if hd_col not in panel_df.columns:
        return {"mw_stat": np.nan, "mw_p_value": np.nan, "domain": domain,
                "n_compressed": 0, "n_non_compressed": 0}

    bm_means = panel_df.groupby("benchmark_id")[hd_col].mean().dropna()
    compressed_hd = bm_means[bm_means.index.isin(compressed_ids)].values
    noncompressed_hd = bm_means[~bm_means.index.isin(compressed_ids)].values

    if len(compressed_hd) < 3 or len(noncompressed_hd) < 3:
        return {"mw_stat": np.nan, "mw_p_value": np.nan, "domain": domain,
                "n_compressed": len(compressed_hd), "n_non_compressed": len(noncompressed_hd)}

    stat, p = scipy.stats.mannwhitneyu(compressed_hd, noncompressed_hd, alternative="greater")
    return {
        "mw_stat": float(stat),
        "mw_p_value": float(p),
        "domain": domain,
        "n_compressed": len(compressed_hd),
        "n_non_compressed": len(noncompressed_hd),
    }


def compute_auc_comparison(
    panel_df: pd.DataFrame,
    domain: str,
    collapse_df: pd.DataFrame,
    lead_months: int = 24,
) -> dict:
    """AUC of H_d(t-lead_months) vs H_d(t) predicting collapse label.
    Returns: {auc_lead, auc_concurrent, domain, lead_months}
    """
    hd_col = f"hd_{domain}"
    if hd_col not in panel_df.columns:
        return {"auc_lead": np.nan, "auc_concurrent": np.nan, "domain": domain, "lead_months": lead_months}

    collapsed_ids = set(collapse_df["benchmark_id"].unique()) if len(collapse_df) > 0 else set()

    bm_stats = panel_df.groupby("benchmark_id")[hd_col].mean().reset_index()
    bm_stats.columns = ["benchmark_id", "hd_mean"]
    bm_stats["collapse_label"] = bm_stats["benchmark_id"].isin(collapsed_ids).astype(int)

    def _get_early_mean(g):
        half = max(1, len(g) // 2)
        return g.sort_values("quarter").iloc[:half][hd_col].mean()

    early = panel_df.groupby("benchmark_id").apply(_get_early_mean).reset_index()
    early.columns = ["benchmark_id", "hd_early"]

    combined = bm_stats.merge(early, on="benchmark_id")
    valid = combined.dropna(subset=["hd_mean", "hd_early", "collapse_label"])

    if len(valid) < 5 or valid["collapse_label"].nunique() < 2:
        return {"auc_lead": np.nan, "auc_concurrent": np.nan, "domain": domain, "lead_months": lead_months}

    auc_concurrent = roc_auc_score(valid["collapse_label"], valid["hd_mean"].fillna(0))
    auc_lead = roc_auc_score(valid["collapse_label"], valid["hd_early"].fillna(0))
    return {"auc_lead": float(auc_lead), "auc_concurrent": float(auc_concurrent),
            "domain": domain, "lead_months": lead_months}


def run_all_statistical_tests(
    panel_df: pd.DataFrame,
    collapse_df: pd.DataFrame,
    compressed_ids,
) -> dict:
    """Run MW + AUC for cv, nlp, tabular.
    Returns: {'cv': {'mw': dict, 'auc': dict}, 'nlp': {...}, 'tabular': {...}}
    """
    result = {}
    for domain in ["cv", "nlp", "tabular"]:
        mw = run_mann_whitney_test(panel_df, domain, compressed_ids)
        auc = compute_auc_comparison(panel_df, domain, collapse_df)
        result[domain] = {"mw": mw, "auc": auc}
        print(f"  {domain}: MW p={mw['mw_p_value']:.4f}, AUC_lead={auc['auc_lead']:.3f}, AUC_conc={auc['auc_concurrent']:.3f}")
    return result
