"""H-M5 Granger Causality: Bidirectional tests per venue."""
import pandas as pd
from statsmodels.tsa.stattools import grangercausalitytests


def granger_per_venue(
    df: pd.DataFrame, cause: str, effect: str, maxlag: int = 2, min_obs: int = 4
) -> dict:
    """Granger test per venue. Returns {venue: {lag: p_value}}."""
    result = {}
    for venue in df.index.get_level_values("venue").unique():
        sub = df.loc[venue].sort_index()
        if len(sub) < min_obs:
            continue
        pair = sub[[effect, cause]].values
        try:
            gc = grangercausalitytests(pair, maxlag, verbose=False)
            result[venue] = {lag: gc[lag][0]["ssr_ftest"][1] for lag in range(1, maxlag + 1)}
        except Exception:
            continue
    return result


def run_bidirectional_granger(df: pd.DataFrame, maxlag: int = 2) -> dict:
    """Test both directions: hhi->entropy and entropy->hhi."""
    fwd = granger_per_venue(df, cause="hhi", effect="entropy", maxlag=maxlag)
    rev = granger_per_venue(df, cause="entropy", effect="hhi", maxlag=maxlag)
    n_sig_fwd = sum(1 for v in fwd if any(p < 0.05 for p in fwd[v].values()))
    n_sig_rev = sum(1 for v in rev if any(p < 0.05 for p in rev[v].values()))
    return {
        "hhi_to_entropy": fwd,
        "entropy_to_hhi": rev,
        "n_significant_forward": n_sig_fwd,
        "n_significant_reverse": n_sig_rev,
    }
