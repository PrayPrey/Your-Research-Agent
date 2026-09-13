"""H-M5 Baseline: Overall Gini series (unified null hypothesis)"""
import pandas as pd
from gini import compute_gini
from config import CONFIG


def compute_overall_gini_series(monthly_df: pd.DataFrame) -> pd.Series:
    """All-modality-combined monthly Gini, DatetimeIndex Series."""
    monthly_gini = {}

    for month, group in monthly_df.groupby("month"):
        counts = group["count"].values
        monthly_gini[month] = compute_gini(counts)

    series = pd.Series(monthly_gini)
    series.index = pd.PeriodIndex(series.index, freq="M")
    series = series.sort_index()
    series.index = series.index.to_timestamp()
    series.name = "overall_gini"

    return series
