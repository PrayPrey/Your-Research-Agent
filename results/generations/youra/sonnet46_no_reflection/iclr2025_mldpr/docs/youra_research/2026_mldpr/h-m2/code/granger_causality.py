"""H-M1: Granger Causality — ADF stationarity, differencing, panel Granger tests."""
import warnings
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import grangercausalitytests, adfuller

warnings.filterwarnings("ignore")


def check_stationarity(series: pd.Series, alpha: float = 0.05) -> bool:
    """ADF test. Returns True if stationary (ADF p < alpha)."""
    clean = series.dropna()
    if len(clean) < 5:
        return True  # too short to test; treat as stationary
    try:
        _, p_value, *_ = adfuller(clean, autolag="AIC")
        return bool(p_value < alpha)
    except Exception:
        return True


def make_stationary(
    series: pd.Series,
    alpha: float = 0.05,
    max_diff: int = 2,
) -> pd.Series:
    """Apply first-order differencing until stationary or max_diff reached.
    Fallback: log-transform then difference if still non-stationary.
    """
    result = series.copy()
    for _ in range(max_diff):
        if check_stationarity(result, alpha):
            return result
        result = result.diff()
    # Fallback: log-transform (handle non-positive values)
    if not check_stationarity(result, alpha):
        shifted = series - series.min() + 1.0
        try:
            log_series = np.log(shifted)
            result = log_series.diff()
        except Exception:
            pass
    return result


def test_granger_causality(
    benchmark_panel: pd.DataFrame,
    max_lag: int = 4,
) -> dict | None:
    """Per-benchmark Granger test: cumulative_count -> score_var_top10.
    Input: DataFrame sorted by quarter with cols [score_var_top10, cumulative_count].
    Returns: {lag: p_value} for lag in 1..max_lag, or None if insufficient data.
    """
    ts = benchmark_panel[["score_var_top10", "cumulative_count"]].copy().dropna()
    if len(ts) < max_lag + 5:
        return None

    # Make each column stationary
    ts_stat = pd.DataFrame(index=ts.index)
    for col in ["score_var_top10", "cumulative_count"]:
        if not check_stationarity(ts[col]):
            ts_stat[col] = make_stationary(ts[col])
        else:
            ts_stat[col] = ts[col]

    ts_stat = ts_stat.dropna()
    if len(ts_stat) < max_lag + 5:
        return None

    try:
        gc_res = grangercausalitytests(
            ts_stat[["score_var_top10", "cumulative_count"]],
            maxlag=max_lag,
            verbose=False,
        )
        return {lag: float(gc_res[lag][0]["ssr_ftest"][1]) for lag in range(1, max_lag + 1)}
    except Exception:
        return None


def test_reverse_causality(
    benchmark_panel: pd.DataFrame,
    max_lag: int = 4,
) -> dict | None:
    """Test compression_event -> cumulative_count direction.
    Input: DataFrame with cols [cumulative_count, compression_event] sorted by quarter.
    Returns: {lag: p_value} or None if insufficient data.
    """
    cols = ["cumulative_count", "compression_event"]
    available = [c for c in cols if c in benchmark_panel.columns]
    if len(available) < 2:
        return None

    ts = benchmark_panel[["compression_event", "cumulative_count"]].copy().dropna()
    if len(ts) < max_lag + 5:
        return None

    ts_stat = pd.DataFrame(index=ts.index)
    for col in ["compression_event", "cumulative_count"]:
        if not check_stationarity(ts[col]):
            ts_stat[col] = make_stationary(ts[col])
        else:
            ts_stat[col] = ts[col]

    ts_stat = ts_stat.dropna()
    if len(ts_stat) < max_lag + 5:
        return None

    try:
        gc_res = grangercausalitytests(
            ts_stat[["cumulative_count", "compression_event"]],
            maxlag=max_lag,
            verbose=False,
        )
        return {lag: float(gc_res[lag][0]["ssr_ftest"][1]) for lag in range(1, max_lag + 1)}
    except Exception:
        return None


def run_granger_panel(
    panel_df: pd.DataFrame,
    max_lag: int = 4,
) -> tuple:
    """Run forward + reverse Granger for all benchmark_ids.
    Returns: (forward_results, reverse_results)
      Each: {benchmark_id: {lag: p_value} | None}
    """
    forward_results: dict = {}
    reverse_results: dict = {}

    benchmark_ids = panel_df["benchmark_id"].unique()
    print(f"  Running Granger tests for {len(benchmark_ids)} benchmarks...")

    for i, benchmark_id in enumerate(benchmark_ids):
        bm_df = panel_df[panel_df["benchmark_id"] == benchmark_id].sort_values("quarter").reset_index(drop=True)
        forward_results[benchmark_id] = test_granger_causality(bm_df, max_lag)
        reverse_results[benchmark_id] = test_reverse_causality(bm_df, max_lag)
        if (i + 1) % 50 == 0:
            n_valid = sum(1 for v in forward_results.values() if v is not None)
            print(f"    Progress: {i+1}/{len(benchmark_ids)}, valid forward: {n_valid}")

    return forward_results, reverse_results


def aggregate_granger_panel(
    granger_results: dict,
    target_lag: int = 2,
) -> dict:
    """Panel-level summary of per-benchmark Granger results.
    Returns: {n_benchmarks_tested, n_significant_lag2, pct_significant_lag2,
              min_p_lag2, median_p_lag2}
    """
    valid = {k: v for k, v in granger_results.items() if v is not None}
    n_tested = len(valid)

    lag_p_values = [v[target_lag] for v in valid.values() if target_lag in v]
    n_significant = sum(1 for p in lag_p_values if p < 0.05)
    pct_significant = n_significant / n_tested if n_tested > 0 else 0.0
    min_p = float(np.min(lag_p_values)) if lag_p_values else None
    median_p = float(np.median(lag_p_values)) if lag_p_values else None

    return {
        "n_benchmarks_tested": n_tested,
        "n_significant_lag2": n_significant,
        "pct_significant_lag2": round(pct_significant, 4),
        "min_p_lag2": min_p,
        "median_p_lag2": median_p,
    }
