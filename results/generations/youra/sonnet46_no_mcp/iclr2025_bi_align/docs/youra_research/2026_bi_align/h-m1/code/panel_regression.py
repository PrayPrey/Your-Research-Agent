# h-m1/code/panel_regression.py
# Panel regression with worker fixed effects for H-M1 dose-response analysis

import logging
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Optional

from config import PANEL_COV_TYPE, RANDOM_SEED

logger = logging.getLogger(__name__)


@dataclass
class PanelResult:
    beta_exposure: float
    p_value: float
    ci_lower: float
    ci_upper: float
    effect_size_per_1k: float
    n_workers: int
    n_obs: int
    model_type: str  # "PanelOLS" | "LSDV" | "calendar_time_ols"
    summary: object = field(default=None, repr=False)


def run_panel_ols(
    panel_df: pd.DataFrame,
    outcome_col: str = "proj_score_z",
    exposure_col: str = "cumulative_tokens_k",
    entity_col: str = "worker_id",
    time_col: str = "session_order",
) -> PanelResult:
    """PanelOLS with EntityEffects + clustered SE. Falls back to LSDV on error."""
    n_workers = panel_df[entity_col].nunique()
    n_obs = len(panel_df)

    try:
        from linearmodels.panel import PanelOLS

        # Ensure MultiIndex
        if not isinstance(panel_df.index, pd.MultiIndex):
            df_idx = panel_df.set_index([entity_col, time_col])
        else:
            df_idx = panel_df

        # Drop rows with NaN in outcome or exposure
        df_idx = df_idx[[outcome_col, exposure_col]].dropna()

        formula = f"{outcome_col} ~ {exposure_col} + EntityEffects"
        res = PanelOLS.from_formula(formula, data=df_idx).fit(
            cov_type="clustered", cluster_entity=True
        )

        beta = float(res.params[exposure_col])
        p_val = float(res.pvalues[exposure_col])
        ci = res.conf_int().loc[exposure_col]
        ci_lower = float(ci.iloc[0])
        ci_upper = float(ci.iloc[1])

        logger.info(f"PanelOLS: beta={beta:.4f}, p={p_val:.4f}, n_workers={n_workers}")
        return PanelResult(
            beta_exposure=beta,
            p_value=p_val,
            ci_lower=ci_lower,
            ci_upper=ci_upper,
            effect_size_per_1k=beta,  # already per 1000 tokens (cumulative_tokens_k units)
            n_workers=n_workers,
            n_obs=n_obs,
            model_type="PanelOLS",
            summary=res,
        )

    except Exception as e:
        logger.warning(f"PanelOLS failed ({e}); falling back to LSDV")
        return run_lsdv_fallback(panel_df, outcome_col, exposure_col, entity_col)


def run_lsdv_fallback(
    panel_df: pd.DataFrame,
    outcome_col: str,
    exposure_col: str,
    entity_col: str,
) -> PanelResult:
    """Least Squares Dummy Variables via statsmodels OLS."""
    import statsmodels.formula.api as smf

    n_workers = panel_df[entity_col].nunique()
    n_obs = len(panel_df)

    df_clean = panel_df[[outcome_col, exposure_col, entity_col]].dropna()

    formula = f"{outcome_col} ~ {exposure_col} + C({entity_col})"
    try:
        res = smf.ols(formula, data=df_clean).fit(
            cov_type="cluster",
            cov_kwds={"groups": df_clean[entity_col]},
        )
        beta = float(res.params[exposure_col])
        p_val = float(res.pvalues[exposure_col])
        ci = res.conf_int().loc[exposure_col]
        ci_lower = float(ci.iloc[0])
        ci_upper = float(ci.iloc[1])
    except Exception as e:
        logger.warning(f"LSDV failed ({e}); returning zero-filled PanelResult")
        beta, p_val, ci_lower, ci_upper = 0.0, 1.0, -1.0, 1.0
        res = None

    logger.info(f"LSDV: beta={beta:.4f}, p={p_val:.4f}, n_workers={n_workers}")
    return PanelResult(
        beta_exposure=beta,
        p_value=p_val,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        effect_size_per_1k=beta,
        n_workers=n_workers,
        n_obs=n_obs,
        model_type="LSDV",
        summary=res,
    )


def between_worker_tercile_comparison(
    panel_df: pd.DataFrame,
    outcome_col: str = "proj_score_z",
    exposure_col: str = "cumulative_tokens_k",
) -> dict:
    """Fallback: split workers into terciles by total cumulative tokens."""
    from scipy import stats

    worker_totals = panel_df.groupby("worker_id")[exposure_col].max()
    try:
        tercile_labels = pd.qcut(worker_totals, q=3, labels=["low", "mid", "high"], duplicates="drop")
    except ValueError:
        # Not enough unique values for 3 bins
        tercile_labels = pd.cut(worker_totals, bins=3, labels=["low", "mid", "high"])

    worker_tercile = tercile_labels.to_dict()
    df = panel_df.copy()
    df["tercile"] = df["worker_id"].map(worker_tercile)
    df = df.dropna(subset=["tercile", outcome_col])

    group_means = df.groupby("tercile")[outcome_col].mean()
    groups = [df[df["tercile"] == t][outcome_col].values for t in ["low", "mid", "high"]]
    groups = [g for g in groups if len(g) > 0]

    if len(groups) >= 2:
        f_stat, p_val = stats.f_oneway(*groups)
    else:
        f_stat, p_val = 0.0, 1.0

    result = {
        "tercile_means": group_means.to_dict(),
        "f_stat": float(f_stat),
        "p_value": float(p_val),
        "n_per_tercile": df.groupby("tercile").size().to_dict(),
    }
    logger.info(f"Tercile comparison: f={f_stat:.3f}, p={p_val:.4f}")
    return result


def bootstrap_beta_ci(
    panel_df: pd.DataFrame,
    n_iter: int = 1000,
    seed: int = RANDOM_SEED,
    outcome_col: str = "proj_score_z",
    exposure_col: str = "cumulative_tokens_k",
    entity_col: str = "worker_id",
) -> tuple:
    """Bootstrap 95% CI on beta_exposure by resampling workers with replacement."""
    rng = np.random.default_rng(seed)
    workers = panel_df[entity_col].unique()
    betas = []

    for _ in range(n_iter):
        sampled_workers = rng.choice(workers, size=len(workers), replace=True)
        parts = []
        for i, w in enumerate(sampled_workers):
            chunk = panel_df[panel_df[entity_col] == w].copy()
            # Give each resampled worker a unique ID to avoid panel index collisions
            chunk[entity_col] = f"boot_{i}"
            chunk["session_order"] = range(len(chunk))
            parts.append(chunk)

        if not parts:
            betas.append(0.0)
            continue

        boot_df = pd.concat(parts, ignore_index=True)
        try:
            result = run_panel_ols(
                boot_df,
                outcome_col=outcome_col,
                exposure_col=exposure_col,
                entity_col=entity_col,
                time_col="session_order",
            )
            betas.append(result.beta_exposure)
        except Exception:
            betas.append(0.0)

    arr = np.array(betas)
    ci_lower = float(np.percentile(arr, 2.5))
    ci_upper = float(np.percentile(arr, 97.5))
    logger.info(f"Bootstrap CI: [{ci_lower:.4f}, {ci_upper:.4f}]")
    return ci_lower, ci_upper


def run_calendar_time_regression(
    panel_df: pd.DataFrame,
    outcome_col: str = "proj_score_z",
    date_col: str = "created_at",
) -> PanelResult:
    """Fallback when worker_id unavailable: OLS on calendar date as exposure proxy."""
    import statsmodels.formula.api as smf

    df = panel_df.copy()
    df["calendar_day"] = pd.to_datetime(df[date_col], errors="coerce")
    df["calendar_day_ordinal"] = df["calendar_day"].apply(
        lambda x: x.toordinal() if pd.notna(x) else np.nan
    )
    df_clean = df[[outcome_col, "calendar_day_ordinal"]].dropna()

    if len(df_clean) < 10:
        logger.warning("Insufficient data for calendar-time regression")
        return PanelResult(0.0, 1.0, -1.0, 1.0, 0.0, 0, len(df), "calendar_time_ols")

    formula = f"{outcome_col} ~ calendar_day_ordinal"
    res = smf.ols(formula, data=df_clean).fit()
    beta = float(res.params["calendar_day_ordinal"])
    p_val = float(res.pvalues["calendar_day_ordinal"])
    ci = res.conf_int().loc["calendar_day_ordinal"]

    return PanelResult(
        beta_exposure=beta,
        p_value=p_val,
        ci_lower=float(ci.iloc[0]),
        ci_upper=float(ci.iloc[1]),
        effect_size_per_1k=beta * 1000,
        n_workers=0,
        n_obs=len(df_clean),
        model_type="calendar_time_ols",
        summary=res,
    )
