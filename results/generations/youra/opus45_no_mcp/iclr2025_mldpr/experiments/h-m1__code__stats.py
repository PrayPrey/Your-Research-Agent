"""Statistical analysis for H-M1 bibliometric study."""
import pandas as pd
from scipy.stats import mannwhitneyu, spearmanr


def compute_ratio(df: pd.DataFrame) -> dict:
    high_avg = df.loc[df.group == "high", "paper_count"].mean()
    low_avg = df.loc[df.group == "low", "paper_count"].mean()
    ratio = high_avg / low_avg if low_avg > 0 else float("inf")
    return {"high_use_avg": high_avg, "low_use_avg": low_avg, "ratio": ratio}


def mannwhitney_test(df: pd.DataFrame) -> dict:
    high = df.loc[df.group == "high", "paper_count"].values
    low = df.loc[df.group == "low", "paper_count"].values
    stat, p = mannwhitneyu(high, low, alternative="greater")
    return {"statistic": float(stat), "p_value": float(p)}


def spearman_correlation(df: pd.DataFrame) -> dict:
    import math
    rho, p = spearmanr(df["run_count"], df["paper_count"])
    rho_val = 0.0 if math.isnan(rho) else float(rho)
    p_val = 1.0 if math.isnan(p) else float(p)
    return {"rho": rho_val, "p_value": p_val}
