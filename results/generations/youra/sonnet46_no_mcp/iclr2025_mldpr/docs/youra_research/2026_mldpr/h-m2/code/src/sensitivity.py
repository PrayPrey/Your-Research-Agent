"""H-M1 sensitivity analysis: SA-1 (F-UJI threshold), SA-2 (PH check), SA-3 (windows)."""
import numpy as np
import pandas as pd
import logging
from src.matching import run_matching
from src.km_analysis import run_km_matched, run_km_unadjusted
from src.cox_analysis import run_cox_primary, check_ph_assumption

logger = logging.getLogger(__name__)


def run_sa1_fuji_threshold(survival_df: pd.DataFrame, cfg) -> dict:
    """SA-1: F-UJI aggregate >= 0.5 threshold split."""
    df = survival_df.copy()
    df["high_findable"] = (df["fair_aggregate"] >= 0.5).astype(int)
    try:
        matched_df, _, meta = run_matching(df, cfg)
        km = run_km_matched(matched_df)
        cox = run_cox_primary(matched_df, predictor_col="findable_score")
        return {"log_rank_p": km["log_rank_p"], "cox_hr": cox["cox_hr"], "label": "sa1"}
    except Exception as e:
        logger.warning(f"SA-1 failed: {e}")
        return {"log_rank_p": np.nan, "cox_hr": np.nan, "label": "sa1", "error": str(e)}


def run_sa2_ph_check(matched_df: pd.DataFrame, cph_model, cfg) -> dict:
    """SA-2: Schoenfeld residuals PH assumption check."""
    result = check_ph_assumption(cph_model, matched_df, p_threshold=getattr(cfg, "SCHOENFELD_ALPHA", 0.05))
    result["label"] = "sa2"
    return result


def run_sa3_observation_windows(
    survival_df: pd.DataFrame,
    cfg,
    windows: list = None,
) -> list:
    """SA-3: Re-run primary analysis with multiple observation windows."""
    if windows is None:
        windows = [180, 365, 730]
    from src.survival_prep import compute_time_to_first_run
    results = []
    for w in windows:
        try:
            df = compute_time_to_first_run(survival_df, observation_window_days=w)
            matched_df, _, meta = run_matching(df, cfg)
            km = run_km_matched(matched_df)
            cox = run_cox_primary(matched_df, predictor_col="findable_score")
            results.append({"window_days": w, "log_rank_p": km["log_rank_p"], "cox_hr": cox["cox_hr"]})
        except Exception as e:
            logger.warning(f"SA-3 window={w} failed: {e}")
            results.append({"window_days": w, "log_rank_p": np.nan, "cox_hr": np.nan, "error": str(e)})
    return results


def run_all_sensitivity(survival_df: pd.DataFrame, matched_df: pd.DataFrame, cph_model, cfg) -> dict:
    """Run SA-1, SA-2, SA-3; return combined dict."""
    return {
        "sa1": run_sa1_fuji_threshold(survival_df, cfg),
        "sa2": run_sa2_ph_check(matched_df, cph_model, cfg),
        "sa3": run_sa3_observation_windows(survival_df, cfg),
    }
