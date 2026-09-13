"""
experiment.py — H-E1: Statistical model fitting and mechanism verification.
"""
from typing import Any

import numpy as np
import pandas as pd
import statsmodels.discrete.conditional_models as cm

# Type alias — runtime class exists; Pyright stubs may not export it directly
ModelResult = Any  # cm.ConditionalLogitResults at runtime

# ---------------------------------------------------------------------------
# Constants (C-E1-2)
# ---------------------------------------------------------------------------
OPTIMIZER: str = "bfgs"
MAX_ITER: int = 200
MIN_CLUSTER_COUNT: int = 100
MIN_PAIRS_PER_CLUSTER: int = 2
MIN_SPLIT_SIZE: int = 1000
MIN_DELTA_AIFS_STD: float = 0.01
MIN_EFFECT_SIZE: float = 1e-6
INTERACTION_TERM: str = "delta_aifs_x_split"


# ---------------------------------------------------------------------------
# Model Fitting (L-3-1)
# ---------------------------------------------------------------------------

def _fit(endog: Any, exog: Any, groups: Any) -> ModelResult:
    model = cm.ConditionalLogit(endog, exog, groups=groups)
    try:
        result = model.fit(method=OPTIMIZER, maxiter=MAX_ITER, disp=False)
    except Exception:
        # Fallback to newton optimizer if bfgs fails to compute covariance
        result = model.fit(method="newton", maxiter=MAX_ITER, disp=False)
    return result


def fit_baseline_model(df_pairs: pd.DataFrame) -> ModelResult:
    """Fit ConditionalLogit: chosen ~ delta_aifs + delta_length, groups=cluster_id."""
    endog = df_pairs["chosen"].to_numpy()
    exog = df_pairs[["delta_aifs", "delta_length"]].to_numpy()
    groups = df_pairs["cluster_id"].to_numpy()
    return _fit(endog, exog, groups)


def fit_proposed_model(df_pairs: pd.DataFrame) -> ModelResult:
    """Fit ConditionalLogit: chosen ~ delta_aifs + delta_length + delta_aifs_x_split."""
    endog = df_pairs["chosen"].to_numpy()
    exog = df_pairs[["delta_aifs", "delta_length", "delta_aifs_x_split"]].to_numpy()
    groups = df_pairs["cluster_id"].to_numpy()
    return _fit(endog, exog, groups)


def fit_extended_model(df_pairs: pd.DataFrame) -> ModelResult:
    """Fit proposed model + supply_prop covariate (supply-side control)."""
    endog = df_pairs["chosen"].to_numpy()
    exog = df_pairs[["delta_aifs", "delta_length", "delta_aifs_x_split", "supply_prop"]].to_numpy()
    groups = df_pairs["cluster_id"].to_numpy()
    return _fit(endog, exog, groups)


def fit_perplexity_model(df_pairs: pd.DataFrame) -> ModelResult:
    """Fit proposed model + delta_log_length covariate (log token length ratio proxy for perplexity)."""
    df = df_pairs.copy()
    if "delta_log_length" not in df.columns:
        # Use log(|delta_length| + 1) * sign as a non-linear perplexity proxy
        # distinct from delta_length to avoid multicollinearity
        raw_sign = np.sign(df["delta_length"].to_numpy())
        raw_sign[raw_sign == 0] = 1
        df["delta_log_length"] = np.log1p(np.abs(df["delta_length"].to_numpy())) * raw_sign
    endog = df["chosen"].to_numpy()
    exog = df[["delta_aifs", "delta_length", "delta_aifs_x_split", "delta_log_length"]].to_numpy()
    groups = df["cluster_id"].to_numpy()
    return _fit(endog, exog, groups)


# ---------------------------------------------------------------------------
# Supply Control
# ---------------------------------------------------------------------------

def compute_supply_prop(df_pairs: pd.DataFrame) -> pd.DataFrame:
    """Add supply_prop column: fraction of online pairs within each cluster_id."""
    df = df_pairs.copy()
    cluster_online = df.groupby("cluster_id")["split"].sum()
    cluster_total = df.groupby("cluster_id")["split"].count()
    supply_prop_map = (cluster_online / cluster_total).to_dict()
    df["supply_prop"] = df["cluster_id"].map(supply_prop_map)
    return df


# ---------------------------------------------------------------------------
# Mechanism Verification (L-3-2)
# ---------------------------------------------------------------------------

def verify_mechanism_activated(
    result: ModelResult,
    df_pairs: pd.DataFrame,
) -> tuple[bool, dict]:
    """Check 5 mechanism indicators. Raises RuntimeError if any is False."""
    indicators: dict[str, bool] = {}

    # 1. beta4_fitted: param index 2 = delta_aifs_x_split, must not be NaN
    try:
        beta4 = float(result.params[2])  # type: ignore[arg-type]
        indicators["beta4_fitted"] = not np.isnan(beta4)
    except (IndexError, KeyError, TypeError):
        beta4 = float("nan")
        indicators["beta4_fitted"] = False

    # 2. data_variance: delta_aifs std > MIN_DELTA_AIFS_STD
    indicators["data_variance"] = float(df_pairs["delta_aifs"].std()) > MIN_DELTA_AIFS_STD

    # 3. split_balanced: both splits have >= MIN_SPLIT_SIZE pairs
    split_counts = df_pairs.groupby("split").size()
    base_count = int(split_counts.get(0, 0))  # type: ignore[arg-type]
    online_count = int(split_counts.get(1, 0))  # type: ignore[arg-type]
    indicators["split_balanced"] = (
        base_count >= MIN_SPLIT_SIZE and online_count >= MIN_SPLIT_SIZE
    )

    # 4. clusters_valid: >= 100 clusters with >= 2 pairs
    counts = df_pairs.groupby("cluster_id").size()
    valid_clusters = int((counts >= MIN_PAIRS_PER_CLUSTER).sum())
    indicators["clusters_valid"] = valid_clusters >= MIN_CLUSTER_COUNT

    # 5. effect_nonzero: |beta4| > MIN_EFFECT_SIZE
    indicators["effect_nonzero"] = (
        indicators["beta4_fitted"] and abs(beta4) > MIN_EFFECT_SIZE
    )

    all_ok = all(indicators.values())
    if not all_ok:
        failed = [k for k, v in indicators.items() if not v]
        raise RuntimeError(
            f"Mechanism verification failed. Failed indicators: {failed}. "
            f"Details: base_pairs={base_count}, online_pairs={online_count}, "
            f"valid_clusters={valid_clusters}"
        )
    return all_ok, indicators
