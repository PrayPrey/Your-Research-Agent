import pandas as pd
import numpy as np
from scipy import stats
from config import REFERENCE_YEAR, MIN_MODELS_PER_COHORT


def compute_reuse_rate(df: pd.DataFrame, reference_year: int = REFERENCE_YEAR,
                       year_col: str = "year_introduced") -> pd.Series:
    """reuse_rate = paper_count / max(1, reference_year - year_introduced)"""
    year = pd.to_numeric(df[year_col], errors="coerce")
    age = (reference_year - year).clip(lower=1)
    rr = df["paper_count"] / age
    rr[year.isna()] = np.nan
    return rr


def compute_rank_reversal_rate(results_df: pd.DataFrame,
                                min_models: int = MIN_MODELS_PER_COHORT) -> pd.Series:
    """
    Per benchmark: split by year cohort, Spearman corr adjacent cohorts,
    rrr = fraction of pairs with corr < 0.5.
    """
    output = {}
    results_df = results_df.dropna(subset=["year", "metric_value"])
    results_df = results_df.copy()
    results_df["year"] = results_df["year"].astype(int)

    for bname, group in results_df.groupby("benchmark_name"):
        years = sorted(group["year"].unique())
        if len(years) < 2:
            output[bname] = float("nan")
            continue

        cohorts = []
        for y in years:
            cohort = group[group["year"] == y].sort_values(
                "metric_value", ascending=False
            )
            if len(cohort) >= min_models:
                cohorts.append(cohort["model"].tolist())

        if len(cohorts) < 2:
            output[bname] = float("nan")
            continue

        reversal_flags = []
        for i in range(len(cohorts) - 1):
            shared = set(cohorts[i]) & set(cohorts[i + 1])
            if len(shared) < min_models:
                continue
            shared = list(shared)
            ranks_a = [cohorts[i].index(m) for m in shared]
            ranks_b = [cohorts[i + 1].index(m) for m in shared]
            if len(set(ranks_a)) < 2 or len(set(ranks_b)) < 2:
                continue
            corr, _ = stats.spearmanr(ranks_a, ranks_b)
            reversal_flags.append(1 if corr < 0.5 else 0)

        if not reversal_flags:
            output[bname] = float("nan")
        else:
            output[bname] = sum(reversal_flags) / len(reversal_flags)

    return pd.Series(output, name="rank_reversal_rate")


def compute_result_cov(results_df: pd.DataFrame) -> pd.Series:
    """CoV (std/mean) of metric_value per benchmark (requires >= 3 rows)."""
    def cov(vals):
        vals = vals.dropna()
        if len(vals) < 3:
            return float("nan")
        mean = vals.mean()
        if mean == 0:
            return float("nan")
        return vals.std(ddof=1) / mean

    return results_df.groupby("benchmark_name")["metric_value"].apply(cov).rename("result_CoV")


def attach_derived(joined_df: pd.DataFrame, results_df: pd.DataFrame,
                   reference_year: int = REFERENCE_YEAR,
                   min_models: int = MIN_MODELS_PER_COHORT) -> pd.DataFrame:
    """Compute all derived variables and merge into joined_df."""
    df = joined_df.copy()

    # reuse_rate
    df["reuse_rate"] = compute_reuse_rate(df, reference_year=reference_year)

    # rank_reversal_rate
    if results_df is not None and not results_df.empty:
        rrr = compute_rank_reversal_rate(results_df, min_models=min_models)
        # results use full benchmark name (with [task] suffix) stored in 'name'
        name_col = "name" if "name" in df.columns else df.columns[0]
        df["rank_reversal_rate"] = df[name_col].map(rrr)

        cov_s = compute_result_cov(results_df)
        df["result_CoV"] = df[name_col].map(cov_s)
    else:
        df["rank_reversal_rate"] = float("nan")
        df["result_CoV"] = float("nan")

    return df
