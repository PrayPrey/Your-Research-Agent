"""Analysis module for H-M3: Chi-square test and share calculations."""

from typing import Literal
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency

from config import SPLIT_DATE, PRE_POST_SPLITS


def assign_period(year_month: str, split_date: str = SPLIT_DATE) -> str:
    """Assign period label based on split date."""
    return "post_2021" if year_month >= split_date else "pre_2021"


def compute_shares(df: pd.DataFrame, split_date: str = SPLIT_DATE) -> pd.DataFrame:
    """Compute period x category totals and emergent share."""
    df = df.copy()
    df["period"] = df["year_month"].apply(lambda x: assign_period(x, split_date))

    period_totals = df.groupby(["period", "category"])["paper_count"].sum().unstack(fill_value=0)

    if "emergent" not in period_totals.columns:
        period_totals["emergent"] = 0
    if "traditional" not in period_totals.columns:
        period_totals["traditional"] = 0

    total = period_totals["emergent"] + period_totals["traditional"]
    period_totals["emergent_share"] = np.where(
        total > 0,
        period_totals["emergent"] / total,
        0.0
    )

    return period_totals


def chi_square_test(period_totals: pd.DataFrame) -> dict:
    """Perform chi-square test for independence."""
    contingency = period_totals[["emergent", "traditional"]].values.astype(float)

    if contingency.sum() == 0 or contingency.shape[0] < 2:
        return {
            "chi2": 0.0,
            "p_value": 1.0,
            "dof": 0,
            "expected": contingency.tolist(),
        }

    if (contingency == 0).any():
        contingency = contingency + 0.5

    try:
        chi2, p_value, dof, expected = chi2_contingency(contingency)
        return {
            "chi2": float(chi2),
            "p_value": float(p_value),
            "dof": int(dof),
            "expected": expected.tolist(),
        }
    except ValueError as e:
        return {
            "chi2": 0.0,
            "p_value": 1.0,
            "dof": 0,
            "expected": contingency.tolist(),
            "error": str(e),
        }


def compare_2024_absolute(df: pd.DataFrame) -> dict:
    """Compare 2024 absolute counts between emergent and traditional."""
    df_2024 = df[df["year_month"].str.startswith("2024")]

    emergent_count = df_2024[df_2024["category"] == "emergent"]["paper_count"].sum()
    traditional_count = df_2024[df_2024["category"] == "traditional"]["paper_count"].sum()

    return {
        "emergent_2024_count": int(emergent_count),
        "traditional_2024_count": int(traditional_count),
        "emergent_exceeds_traditional_2024": emergent_count > traditional_count,
    }


def analyze_attention_shift(df: pd.DataFrame, split_date: str = SPLIT_DATE) -> dict:
    """Full analysis pipeline for researcher attention shift."""
    df_filtered = df[df["category"].isin(["emergent", "traditional"])].copy()

    if len(df_filtered) == 0:
        return {
            "pre_2021_emergent_share": 0.0,
            "post_2021_emergent_share": 0.0,
            "share_increase": 0.0,
            "chi2_statistic": 0.0,
            "p_value": 1.0,
            "emergent_exceeds_traditional_2024": False,
            "emergent_2024_count": 0,
            "traditional_2024_count": 0,
            "error": "No data found for emergent or traditional benchmarks",
        }

    period_totals = compute_shares(df_filtered, split_date)

    pre_share = period_totals.loc["pre_2021", "emergent_share"] if "pre_2021" in period_totals.index else 0.0
    post_share = period_totals.loc["post_2021", "emergent_share"] if "post_2021" in period_totals.index else 0.0

    chi_result = chi_square_test(period_totals)
    absolute_result = compare_2024_absolute(df_filtered)

    return {
        "pre_2021_emergent_share": float(pre_share),
        "post_2021_emergent_share": float(post_share),
        "share_increase": float(post_share - pre_share),
        "chi2_statistic": chi_result["chi2"],
        "p_value": chi_result["p_value"],
        "dof": chi_result["dof"],
        "expected": chi_result["expected"],
        **absolute_result,
    }


def run_ablation_time_windows(df: pd.DataFrame) -> dict[str, dict]:
    """Run analysis across multiple split dates for sensitivity."""
    results = {}
    for split in PRE_POST_SPLITS:
        results[split] = analyze_attention_shift(df, split_date=split)
    return results
