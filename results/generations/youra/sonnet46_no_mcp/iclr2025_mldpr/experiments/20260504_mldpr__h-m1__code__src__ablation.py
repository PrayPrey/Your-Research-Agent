"""H-M1 ablation runner: A (FAIR threshold), B (accessible IV), C (relaxed caliper)."""
import numpy as np
import pandas as pd
import logging
from src.matching import run_matching
from src.km_analysis import run_km_matched
from src.cox_analysis import run_cox_primary
from src.findable import compute_accessible_score

logger = logging.getLogger(__name__)


def run_ablation_a(survival_df: pd.DataFrame, cfg) -> dict:
    """Ablation A: fair_proxy_score >= 0.5 binary split instead of median Findable split."""
    df = survival_df.copy()
    df["treatment"] = (df["fair_aggregate"] >= 0.5).astype(int)
    df["high_findable"] = df["treatment"]
    try:
        matched_df, smd_df, meta = run_matching(df, cfg)
        km = run_km_matched(matched_df)
        cox = run_cox_primary(matched_df, predictor_col="findable_score")
        return {
            "log_rank_p": km["log_rank_p"],
            "cox_hr": cox["cox_hr"],
            "n_matched_pairs": meta["n_matched_pairs"],
            "smd_max": meta["smd_max"],
            "label": "ablation_a",
        }
    except Exception as e:
        logger.warning(f"Ablation A failed: {e}")
        return {"log_rank_p": np.nan, "cox_hr": np.nan, "n_matched_pairs": 0, "smd_max": np.nan, "label": "ablation_a", "error": str(e)}


def run_ablation_b(survival_df: pd.DataFrame, cfg) -> dict:
    """Ablation B: accessible_score as alternative IV."""
    df = survival_df.copy()
    accessible = compute_accessible_score(df)
    df["accessible_score"] = accessible
    median_a = accessible.median()
    df["high_findable"] = (accessible > median_a).astype(int)
    try:
        matched_df, smd_df, meta = run_matching(df, cfg)
        km = run_km_matched(matched_df)
        # Use accessible_score as predictor in Cox
        if "accessible_score" not in matched_df.columns:
            matched_df["accessible_score"] = df.loc[matched_df.index, "accessible_score"] if len(matched_df) > 0 else 0.0
        try:
            cox = run_cox_primary(matched_df, predictor_col="accessible_score")
        except Exception:
            cox = {"cox_hr": np.nan}
        return {
            "log_rank_p": km["log_rank_p"],
            "cox_hr": cox["cox_hr"],
            "n_matched_pairs": meta["n_matched_pairs"],
            "smd_max": meta["smd_max"],
            "label": "ablation_b",
        }
    except Exception as e:
        logger.warning(f"Ablation B failed: {e}")
        return {"log_rank_p": np.nan, "cox_hr": np.nan, "n_matched_pairs": 0, "smd_max": np.nan, "label": "ablation_b", "error": str(e)}


def run_ablation_c(survival_df: pd.DataFrame, cfg) -> dict:
    """Ablation C: relaxed caliper (0.3*SD) + ratio=5 matching for robustness."""
    try:
        relaxed_factor = getattr(cfg, "CALIPER_RELAXED_FACTOR", 0.3)
        matched_df, smd_df, meta = run_matching(survival_df, cfg, caliper_factor=relaxed_factor, ratio=5)
        km = run_km_matched(matched_df)
        cox = run_cox_primary(matched_df, predictor_col="findable_score")
        return {
            "log_rank_p": km["log_rank_p"],
            "cox_hr": cox["cox_hr"],
            "n_matched_pairs": meta["n_matched_pairs"],
            "smd_max": meta["smd_max"],
            "label": "ablation_c",
        }
    except Exception as e:
        logger.warning(f"Ablation C failed: {e}")
        return {"log_rank_p": np.nan, "cox_hr": np.nan, "n_matched_pairs": 0, "smd_max": np.nan, "label": "ablation_c", "error": str(e)}


def run_all_ablations(survival_df: pd.DataFrame, cfg) -> dict:
    """Run A, B, C sequentially; return {label: result_dict}."""
    results = {}
    for fn, label in [(run_ablation_a, "ablation_a"), (run_ablation_b, "ablation_b"), (run_ablation_c, "ablation_c")]:
        r = fn(survival_df, cfg)
        results[label] = r
    return results
