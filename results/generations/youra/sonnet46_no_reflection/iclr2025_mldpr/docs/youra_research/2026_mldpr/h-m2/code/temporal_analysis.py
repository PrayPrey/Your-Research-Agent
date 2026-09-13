"""H-M2: Temporal Analysis + Kaplan-Meier Lead Time."""
import numpy as np
import pandas as pd

DOMAIN_THRESHOLDS: dict = {"cv": 0.5, "nlp": 0.3, "tabular": 0.90}


def compute_signal_onset_times(
    panel_df: pd.DataFrame,
    domain: str,
    compression_mask,
    collapse_df: pd.DataFrame,
) -> pd.DataFrame:
    """Find first quarter H_d exceeds domain threshold; compute lead_months to collapse.
    Returns: DataFrame[benchmark_id, lead_months, onset_observed, domain]
    """
    hd_col = f"hd_{domain}"
    threshold = DOMAIN_THRESHOLDS.get(domain, 0.5)
    compressed_panel = panel_df[panel_df["benchmark_id"].isin(compression_mask)].copy()
    onset_records = []

    for bm_id, bm_data in compressed_panel.groupby("benchmark_id"):
        bm_sorted = bm_data.sort_values("quarter").reset_index(drop=True)

        collapse_row = collapse_df[collapse_df["benchmark_id"] == bm_id]
        if collapse_row.empty or hd_col not in bm_sorted.columns:
            onset_records.append({"benchmark_id": bm_id, "lead_months": None,
                                   "onset_observed": False, "domain": domain})
            continue

        collapse_q = str(collapse_row["collapse_quarter"].iloc[0])
        hd_vals = bm_sorted[hd_col]

        if hd_vals.isna().all():
            onset_records.append({"benchmark_id": bm_id, "lead_months": None,
                                   "onset_observed": False, "domain": domain})
            continue

        onset_mask = hd_vals > threshold
        if not onset_mask.any():
            onset_records.append({"benchmark_id": bm_id, "lead_months": None,
                                   "onset_observed": False, "domain": domain})
            continue

        onset_q = str(bm_sorted[onset_mask]["quarter"].iloc[0])

        try:
            lead_months = (pd.Period(collapse_q, "Q") - pd.Period(onset_q, "Q")).n * 3
            onset_observed = lead_months >= 0
        except Exception:
            lead_months = None
            onset_observed = False

        onset_records.append({"benchmark_id": bm_id, "lead_months": lead_months,
                               "onset_observed": onset_observed, "domain": domain})

    if not onset_records:
        return pd.DataFrame(columns=["benchmark_id", "lead_months", "onset_observed", "domain"])
    return pd.DataFrame(onset_records)


def run_temporal_ordering_test(
    onset_df: pd.DataFrame,
    min_lead_months: int = 12,
) -> dict:
    """KM estimator fit + fraction_leading computation.
    Returns: {fraction_leading, median_lead_months, km_estimator, n_events, n_censored}
    """
    from lifelines import KaplanMeierFitter

    T = onset_df["lead_months"].fillna(0).clip(lower=0)
    E = onset_df["onset_observed"].astype(int)

    kmf = KaplanMeierFitter()
    if len(T) > 0 and E.sum() > 0:
        kmf.fit(T, event_observed=E, label="lead_time")
    else:
        kmf.fit([0], event_observed=[0], label="lead_time")

    observed = onset_df[onset_df["onset_observed"] == True]
    fraction_leading = 0.0
    if len(observed) > 0:
        valid_lead = observed["lead_months"].dropna()
        if len(valid_lead) > 0:
            fraction_leading = float((valid_lead >= min_lead_months).mean())

    return {
        "fraction_leading": fraction_leading,
        "median_lead_months": float(kmf.median_survival_time_) if not np.isnan(kmf.median_survival_time_) else 0.0,
        "km_estimator": kmf,
        "n_events": int(E.sum()),
        "n_censored": int((E == 0).sum()),
    }


def compute_onset_for_all_domains(
    panel_df: pd.DataFrame,
    collapse_df: pd.DataFrame,
    compression_mask,
) -> dict:
    """Run compute_signal_onset_times for each of cv, nlp, tabular.
    Returns: {'cv': onset_df, 'nlp': onset_df, 'tabular': onset_df}
    """
    result = {}
    for domain in ["cv", "nlp", "tabular"]:
        hd_col = f"hd_{domain}"
        if hd_col not in panel_df.columns or panel_df[hd_col].isna().all():
            print(f"⚠ Skipping domain '{domain}': hd_{domain} all-NaN")
            result[domain] = pd.DataFrame(columns=["benchmark_id", "lead_months", "onset_observed", "domain"])
            continue

        onset_df = compute_signal_onset_times(panel_df, domain, compression_mask, collapse_df)
        result[domain] = onset_df
        n_obs = onset_df["onset_observed"].sum() if len(onset_df) > 0 else 0
        print(f"  Domain {domain}: {len(onset_df)} benchmarks, {n_obs} onset events observed")

    return result
