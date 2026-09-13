"""H-M1 Kaplan-Meier survival analysis: unadjusted baseline and matched analysis."""
import numpy as np
import pandas as pd
import logging
from lifelines import KaplanMeierFitter, CoxPHFitter
from lifelines.statistics import logrank_test

logger = logging.getLogger(__name__)


def run_km_unadjusted(
    survival_df: pd.DataFrame,
    treatment_col: str = "high_findable",
) -> dict:
    """Unadjusted KM analysis (baseline — no propensity matching)."""
    high = survival_df[survival_df[treatment_col] == 1]
    low = survival_df[survival_df[treatment_col] == 0]
    kmf_high = KaplanMeierFitter()
    kmf_low = KaplanMeierFitter()
    kmf_high.fit(high["time_to_first_run"], event_observed=high["event"], label="high_findable")
    kmf_low.fit(low["time_to_first_run"], event_observed=low["event"], label="low_findable")
    lr = logrank_test(
        high["time_to_first_run"], low["time_to_first_run"],
        event_observed_A=high["event"], event_observed_B=low["event"]
    )
    median_high = float(kmf_high.median_survival_time_)
    median_low = float(kmf_low.median_survival_time_)
    baseline_p = float(lr.p_value)
    logger.info(f"Unadjusted KM: log_rank_p={baseline_p:.4f}, median_high={median_high:.1f}, median_low={median_low:.1f}")
    return {
        "baseline_log_rank_p": baseline_p,
        "median_ttfr_high_unadj": median_high,
        "median_ttfr_low_unadj": median_low,
        "kmf_high": kmf_high,
        "kmf_low": kmf_low,
    }


def run_km_matched(
    matched_df: pd.DataFrame,
    treatment_col: str = "high_findable",
) -> dict:
    """Matched KM analysis (proposed) — PRIMARY GATE."""
    high = matched_df[matched_df[treatment_col] == 1]
    low = matched_df[matched_df[treatment_col] == 0]
    kmf_high = KaplanMeierFitter()
    kmf_low = KaplanMeierFitter()
    kmf_high.fit(high["time_to_first_run"], event_observed=high["event"], label="high_findable")
    kmf_low.fit(low["time_to_first_run"], event_observed=low["event"], label="low_findable")
    lr = logrank_test(
        high["time_to_first_run"], low["time_to_first_run"],
        event_observed_A=high["event"], event_observed_B=low["event"]
    )
    log_rank_p = float(lr.p_value)
    median_high = float(kmf_high.median_survival_time_)
    median_low = float(kmf_low.median_survival_time_)
    logger.info(f"Matched KM: log_rank_p={log_rank_p:.4f}, median_high={median_high:.1f}, median_low={median_low:.1f}")
    return {
        "log_rank_p": log_rank_p,
        "median_ttfr_high": median_high,
        "median_ttfr_low": median_low,
        "kmf_high": kmf_high,
        "kmf_low": kmf_low,
    }
