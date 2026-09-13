"""H-M5 Models: Panel regression implementations."""
import pandas as pd
import statsmodels.api as sm
from linearmodels.panel import PooledOLS, PanelOLS


def fit_baseline(df: pd.DataFrame, hhi_col: str = "hhi_lag1") -> dict:
    """Pooled OLS: entropy ~ const + hhi_lag1 + paper_count, no FE."""
    y = df["entropy"]
    X = sm.add_constant(df[[hhi_col, "paper_count"]])
    res = PooledOLS(y, X).fit()
    ci = res.conf_int().loc[hhi_col]
    return {
        "beta": float(res.params[hhi_col]),
        "p_value": float(res.pvalues[hhi_col]),
        "r_squared": float(res.rsquared),
        "conf_int": [float(ci["lower"]), float(ci["upper"])],
    }


def fit_panel_fe(
    df: pd.DataFrame,
    hhi_col: str = "hhi_lag1",
    entity_effects: bool = True,
    time_effects: bool = True,
) -> dict:
    """PanelOLS with entity/time FE and clustered SE."""
    y = df["entropy"]
    X = sm.add_constant(df[[hhi_col, "paper_count"]])
    mod = PanelOLS(y, X, entity_effects=entity_effects, time_effects=time_effects)
    res = mod.fit(cov_type="clustered", cluster_entity=True)
    ci = res.conf_int().loc[hhi_col]
    return {
        "beta": float(res.params[hhi_col]),
        "p_value": float(res.pvalues[hhi_col]),
        "conf_int_lower": float(ci["lower"]),
        "conf_int_upper": float(ci["upper"]),
        "r_squared": float(res.rsquared),
        "n_obs": int(res.nobs),
        "results_obj": res,
    }


def fit_delta_spec(df: pd.DataFrame) -> dict:
    """Delta robustness: delta_entropy ~ const + delta_hhi (lagged)."""
    df = df.copy()
    df["delta_hhi_lag1"] = df.groupby(level="venue")["delta_hhi"].shift(1)
    df = df.dropna()
    if len(df) < 3:
        return {"beta": None, "p_value": None, "r_squared": None, "conf_int": None, "error": "insufficient data"}
    y = df["delta_entropy"]
    X = sm.add_constant(df[["delta_hhi_lag1"]])
    res = PooledOLS(y, X).fit()
    ci = res.conf_int().loc["delta_hhi_lag1"]
    return {
        "beta": float(res.params["delta_hhi_lag1"]),
        "p_value": float(res.pvalues["delta_hhi_lag1"]),
        "r_squared": float(res.rsquared),
        "conf_int": [float(ci["lower"]), float(ci["upper"])],
    }


def run_robustness_suite(df_lag1: pd.DataFrame, df_lag2: pd.DataFrame) -> dict:
    """Run 3 robustness specs: lag2, entity-only, delta."""
    return {
        "lag2": fit_panel_fe(df_lag2, hhi_col="hhi_lag2"),
        "entity_only": fit_panel_fe(df_lag1, time_effects=False),
        "delta_spec": fit_delta_spec(df_lag1),
    }
