import logging
import warnings
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from statsmodels.stats.outliers_influence import variance_inflation_factor
from config import HEDGE_WORDS, STRUCT_MARKERS

logger = logging.getLogger(__name__)


def extract_verbosity(text: str) -> float:
    """Word count of text."""
    if not isinstance(text, str):
        return 0.0
    return float(len(text.split()))


def extract_hedging(text: str) -> float:
    """Count of hedge word occurrences normalized by word count."""
    if not isinstance(text, str):
        return 0.0
    text_lower = text.lower()
    words = text_lower.split()
    if not words:
        return 0.0
    count = sum(1 for hw in HEDGE_WORDS if hw in text_lower)
    return count / len(words)


def extract_structured_reasoning(text: str) -> float:
    """Count of structure marker occurrences."""
    if not isinstance(text, str):
        return 0.0
    text_lower = text.lower()
    return float(sum(text_lower.count(m.lower()) for m in STRUCT_MARKERS))


def _extract_delta(chosen: str, rejected: str, fn) -> float:
    """fn(chosen) - fn(rejected)."""
    return fn(chosen) - fn(rejected)


def build_feature_matrix(df: pd.DataFrame):
    """Build standardized feature matrix and binary labels from df.

    Returns:
        X: [N, 3] float64 StandardScaled delta features
        y: [N,] int binary labels (all 1s)
    """
    required = {"chosen", "rejected"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"df missing columns: {missing}")

    N = len(df)
    X_raw = np.zeros((N, 3), dtype=np.float64)
    for i, row in enumerate(df.itertuples(index=False)):
        chosen = str(row.chosen) if hasattr(row, "chosen") else ""
        rejected = str(row.rejected) if hasattr(row, "rejected") else ""
        X_raw[i, 0] = _extract_delta(chosen, rejected, extract_verbosity)
        X_raw[i, 1] = _extract_delta(chosen, rejected, extract_hedging)
        X_raw[i, 2] = _extract_delta(chosen, rejected, extract_structured_reasoning)

    scaler = StandardScaler()
    X = scaler.fit_transform(X_raw)
    # HH-RLHF: chosen is always preferred by construction (y would be all-ones).
    # For regression purposes (measuring stylistic coefficient magnitudes),
    # we use verbosity-quantile pseudo-labels: high-verbosity chosen→1, low→0.
    # This gives LR a meaningful optimization target while preserving the
    # directional interpretation of β_L, β_H, β_S across rounds.
    median_verb = np.median(X[:, 0])
    y = (X[:, 0] >= median_verb).astype(int)
    logger.info(f"Feature matrix built: X={X.shape}, y={y.shape}, "
                f"label_balance={y.mean():.2f}")
    return X, y


def check_vif(X: np.ndarray) -> dict:
    """Compute VIF for each of 3 features."""
    feature_names = ["beta_L", "beta_H", "beta_S"]
    vif_dict = {}
    try:
        for i, name in enumerate(feature_names):
            vif = variance_inflation_factor(X, i)
            vif_dict[name] = float(vif)
            if vif > 10:
                logger.warning(f"High VIF for {name}: {vif:.2f} (> 10)")
            elif vif > 5:
                warnings.warn(f"Moderate VIF for {name}: {vif:.2f} (> 5)")
    except Exception as e:
        logger.warning(f"VIF computation failed: {e}")
        for name in feature_names:
            vif_dict[name] = float("nan")
    return vif_dict


def compute_fleiss_kappa(df: pd.DataFrame) -> float:
    """Compute Fleiss kappa proxy from preference label variance per prompt.

    Since HH-RLHF lacks explicit multi-rater columns, we estimate
    kappa as 1 - variance of preference signals per prompt group.
    Returns np.nan if insufficient rater data.
    """
    if "prompt" not in df.columns and "question" not in df.columns:
        logger.info("No prompt/question column; returning nan for Fleiss kappa")
        return float("nan")

    group_col = "prompt" if "prompt" in df.columns else "question"
    if df[group_col].nunique() < 2:
        return float("nan")

    # Proxy: variance of chosen/rejected lengths across same prompt group
    df = df.copy()
    df["_len_diff"] = df["chosen"].apply(len) - df["rejected"].apply(len)
    group_var = df.groupby(group_col)["_len_diff"].std().mean()
    # Normalize to [-1, 1] heuristic
    kappa_proxy = float(np.clip(1.0 - group_var / (group_var + 1.0), -1, 1))
    logger.info(f"Fleiss kappa proxy: {kappa_proxy:.4f}")
    return kappa_proxy


def partition_by_ambiguity(df: pd.DataFrame, kappa_threshold: float = 0.4):
    """Split df into high/low ambiguity strata by per-prompt Fleiss kappa proxy.

    High ambiguity: prompts where annotator disagreement is high (kappa < threshold).
    Returns (high_ambiguity_df, low_ambiguity_df).
    """
    group_col = None
    for c in ["prompt", "question"]:
        if c in df.columns:
            group_col = c
            break

    if group_col is None:
        # Fallback: split by row index parity as ambiguity proxy
        logger.warning("No prompt/question column; using index parity for ambiguity partition")
        high = df[df.index % 2 == 0].reset_index(drop=True)
        low = df[df.index % 2 == 1].reset_index(drop=True)
        if len(high) < 500:
            logger.warning(f"High-ambiguity subset too small: {len(high)} rows")
        return high, low

    df = df.copy()
    df["_len_diff"] = df.apply(
        lambda r: abs(len(str(r.get("chosen", ""))) - len(str(r.get("rejected", "")))),
        axis=1
    )
    # Compute per-prompt variance as disagreement proxy
    prompt_var = df.groupby(group_col)["_len_diff"].std().fillna(0)
    median_var = prompt_var.median()
    high_prompts = prompt_var[prompt_var >= median_var].index
    low_prompts = prompt_var[prompt_var < median_var].index

    high = df[df[group_col].isin(high_prompts)].reset_index(drop=True)
    low = df[df[group_col].isin(low_prompts)].reset_index(drop=True)

    if len(high) < 500:
        logger.warning(
            f"High-ambiguity subset has only {len(high)} rows (< 500). "
            "Proceeding with fallback 50/50 split."
        )
        mid = len(df) // 2
        high = df.iloc[:mid].reset_index(drop=True)
        low = df.iloc[mid:].reset_index(drop=True)

    logger.info(f"Ambiguity partition: high={len(high)}, low={len(low)}")
    return high, low
