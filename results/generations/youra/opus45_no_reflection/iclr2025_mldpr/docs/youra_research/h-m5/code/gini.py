"""H-M5 Gini Coefficient: Computation and time series construction"""
import numpy as np
import pandas as pd
from config import CONFIG


def compute_gini(counts: np.ndarray) -> float:
    """Gini coefficient of a 1D count array. NaN if empty, 0.0 if single element."""
    counts = np.asarray(counts, dtype=float)
    counts = counts[~np.isnan(counts)]
    counts = counts[counts > 0]

    if len(counts) == 0:
        return np.nan
    if len(counts) == 1:
        return 0.0
    if counts.sum() == 0:
        return np.nan

    sorted_counts = np.sort(counts)
    n = len(sorted_counts)
    cumsum = np.cumsum(sorted_counts)
    gini = (2 * np.sum(np.arange(1, n + 1) * sorted_counts)) / (n * cumsum[-1]) - (n + 1) / n
    return float(gini)


def compute_modality_gini_series(monthly_df: pd.DataFrame) -> pd.DataFrame:
    """monthly_df: month,modality,benchmark,count -> DatetimeIndex, cols=[CV,NLP,Audio,Tabular]."""
    modalities = ["CV", "NLP", "Audio", "Tabular"]

    gini_data = {}

    for modality in modalities:
        mod_df = monthly_df[monthly_df["modality"] == modality]

        monthly_gini = {}
        for month, group in mod_df.groupby("month"):
            counts = group["count"].values
            monthly_gini[month] = compute_gini(counts)

        gini_data[modality] = monthly_gini

    gini_df = pd.DataFrame(gini_data)
    gini_df.index = pd.PeriodIndex(gini_df.index, freq="M")
    gini_df = gini_df.sort_index()
    gini_df.index = gini_df.index.to_timestamp()

    all_months = pd.date_range(CONFIG.date_start, CONFIG.date_end, freq="MS")
    gini_df = gini_df.reindex(all_months)

    gini_df = gini_df[modalities]

    print(f"Gini time series: {len(gini_df)} time points, modalities: {list(gini_df.columns)}")

    if len(gini_df) < CONFIG.min_time_points:
        print(f"Warning: Only {len(gini_df)} time points (expected >= {CONFIG.min_time_points})")

    return gini_df
