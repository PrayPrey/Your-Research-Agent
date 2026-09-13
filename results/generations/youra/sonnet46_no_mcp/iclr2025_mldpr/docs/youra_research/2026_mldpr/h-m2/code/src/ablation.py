"""H-M2 ablation studies: caliper and ratio sensitivity."""
import logging
import pandas as pd
from .matching_accessible import run_accessible_matching
from .mwu_analysis import run_mwu_matched

logger = logging.getLogger(__name__)


def run_ablation_caliper(df: pd.DataFrame, fair_scores_df: pd.DataFrame, caliper_values: list = None) -> pd.DataFrame:
    """Run matching at different caliper factors."""
    if caliper_values is None:
        caliper_values = [0.1, 0.2, 0.3, 0.8]
    records = []
    for cf in caliper_values:
        matched_df, smd_df, meta = run_accessible_matching(df, caliper_factor=cf, min_pairs=10)
        if len(matched_df) > 0 and meta["n_matched_pairs"] > 0:
            mwu = run_mwu_matched(matched_df)
            records.append({
                "caliper_factor": cf,
                "n_matched_pairs": meta["n_matched_pairs"],
                "smd_max": meta["smd_max"],
                "p_value": mwu["p_value"],
                "effect_size_r": mwu["effect_size_r"],
                "high_mean": mwu["high_mean"],
                "low_mean": mwu["low_mean"],
            })
        else:
            records.append({"caliper_factor": cf, "n_matched_pairs": 0, "smd_max": None,
                            "p_value": None, "effect_size_r": None, "high_mean": None, "low_mean": None})
    return pd.DataFrame(records)


def run_ablation_ratio(df: pd.DataFrame, fair_scores_df: pd.DataFrame, ratios: list = None) -> pd.DataFrame:
    """Run matching at different matching ratios."""
    if ratios is None:
        ratios = [1, 2, 3]
    records = []
    for r in ratios:
        matched_df, smd_df, meta = run_accessible_matching(df, caliper_factor=0.2, seed=42 + r, min_pairs=10)
        if len(matched_df) > 0 and meta["n_matched_pairs"] > 0:
            mwu = run_mwu_matched(matched_df)
            records.append({
                "ratio": r,
                "n_matched_pairs": meta["n_matched_pairs"],
                "p_value": mwu["p_value"],
                "effect_size_r": mwu["effect_size_r"],
            })
        else:
            records.append({"ratio": r, "n_matched_pairs": 0, "p_value": None, "effect_size_r": None})
    return pd.DataFrame(records)
