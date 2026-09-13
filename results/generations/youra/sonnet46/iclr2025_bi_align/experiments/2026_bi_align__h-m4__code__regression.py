"""
regression.py - 4-stage OLS mediation pipeline for h-m4.

Implements:
  Stage 1: PM-only model (C_sem ~ pm_proxy + tier dummies)
  Stage 2: Full model (C_sem ~ pm_proxy + 5 surface features + tier dummies)
  Stage 3: Robustness model (tier_rank replaces pm_proxy)
  Stage 4: Mediation proportion computation
All models use HC3 heteroscedasticity-robust standard errors.
"""
import logging
import numpy as np
import pandas as pd
import statsmodels.api as sm
from dataclasses import dataclass, field
from statsmodels.stats.outliers_influence import variance_inflation_factor
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

SURFACE_FEATURE_COLS = ['response_length', 'bullet_density', 'politeness_freq', 'ttr', 'mean_sent_len']
TIER_RANK_MAP = {'helpful-base': 1, 'helpful-rejection-sampled': 2, 'helpful-online': 3}


@dataclass
class OLSStageResult:
    """Results from a single OLS regression stage."""
    model_name: str
    stage: str            # 'pm_only' | 'full' | 'robustness'
    beta_pm: float
    p_pm: float
    beta_pm_ci: Tuple[float, float]   # (lower, upper) 95% CI
    r_squared: float
    nobs: int
    all_params: Dict[str, float]
    all_pvalues: Dict[str, float]
    all_ci: Dict[str, Tuple[float, float]]
    condition_number: float


@dataclass
class MediationResult:
    """Aggregated mediation analysis results for one SBERT model."""
    model_name: str
    beta_pm_reduced: float
    beta_pm_full: float
    mediation_ratio: float          # (beta_pm_reduced - beta_pm_full) / beta_pm_reduced
    pm_effect_retained: float       # |beta_pm_full / beta_pm_reduced|
    stage_pm_only: OLSStageResult
    stage_full: OLSStageResult
    stage_robustness: OLSStageResult


def _extract_stage_result(
    fitted_model,
    model_name: str,
    stage: str,
    pm_col: str = 'pm_proxy',
) -> OLSStageResult:
    """Extract OLSStageResult from a fitted statsmodels OLS result."""
    params = fitted_model.params.to_dict()
    pvalues = fitted_model.pvalues.to_dict()
    conf_int = fitted_model.conf_int()
    all_ci = {k: (float(conf_int.loc[k, 0]), float(conf_int.loc[k, 1]))
              for k in conf_int.index}

    if pm_col in params:
        beta_pm = float(params[pm_col])
        p_pm = float(pvalues[pm_col])
        beta_pm_ci = all_ci.get(pm_col, (float('nan'), float('nan')))
    else:
        beta_pm = float('nan')
        p_pm = float('nan')
        beta_pm_ci = (float('nan'), float('nan'))

    try:
        cond_num = float(fitted_model.condition_number)
    except Exception:
        cond_num = float('nan')

    return OLSStageResult(
        model_name=model_name,
        stage=stage,
        beta_pm=beta_pm,
        p_pm=p_pm,
        beta_pm_ci=beta_pm_ci,
        r_squared=float(fitted_model.rsquared),
        nobs=int(fitted_model.nobs),
        all_params={k: float(v) for k, v in params.items()},
        all_pvalues={k: float(v) for k, v in pvalues.items()},
        all_ci={k: (float(v[0]), float(v[1])) for k, v in all_ci.items()},
        condition_number=cond_num,
    )


def run_pm_only_model(df: pd.DataFrame, cov_type: str = 'HC3', model_name: str = '') -> OLSStageResult:
    """Stage 1: C_sem ~ const + pm_proxy + tier_T2 + tier_T3 (HC3 SE).

    Tier dummies via pd.get_dummies(drop_first=True), T1=reference (helpful-base).

    Args:
        df: DataFrame with columns: tier, pm_proxy, c_sem
        cov_type: Covariance type for robust SE (default 'HC3')
        model_name: SBERT model name for result labeling

    Returns:
        OLSStageResult for Stage 1
    """
    tier_dummies = pd.get_dummies(df['tier'], prefix='tier', drop_first=True).astype(float)
    X = sm.add_constant(pd.concat([df[['pm_proxy']], tier_dummies], axis=1))
    y = df['c_sem']
    res = sm.OLS(y, X).fit(cov_type=cov_type)
    logger.debug(f"[Stage1] nobs={int(res.nobs)}, beta_pm={res.params.get('pm_proxy', float('nan')):.4f}")
    return _extract_stage_result(res, model_name, 'pm_only', pm_col='pm_proxy')


def run_full_model(df: pd.DataFrame, cov_type: str = 'HC3', model_name: str = '') -> OLSStageResult:
    """Stage 2: C_sem ~ const + pm_proxy + 5 surface features + tier dummies (HC3 SE).

    Args:
        df: DataFrame with columns: tier, pm_proxy, c_sem, + SURFACE_FEATURE_COLS
        cov_type: Covariance type for robust SE
        model_name: SBERT model name for result labeling

    Returns:
        OLSStageResult for Stage 2
    """
    tier_dummies = pd.get_dummies(df['tier'], prefix='tier', drop_first=True).astype(float)
    predictors = df[['pm_proxy'] + SURFACE_FEATURE_COLS].copy()
    X = sm.add_constant(pd.concat([predictors, tier_dummies], axis=1))
    y = df['c_sem']
    res = sm.OLS(y, X).fit(cov_type=cov_type)
    logger.debug(f"[Stage2] nobs={int(res.nobs)}, beta_pm={res.params.get('pm_proxy', float('nan')):.4f}")
    return _extract_stage_result(res, model_name, 'full', pm_col='pm_proxy')


def run_robustness_model(df: pd.DataFrame, cov_type: str = 'HC3', model_name: str = '') -> OLSStageResult:
    """Stage 3: Replace pm_proxy with tier_rank (ordinal 1/2/3) + surface features.

    Args:
        df: DataFrame with columns: tier, c_sem, + SURFACE_FEATURE_COLS
        cov_type: Covariance type for robust SE
        model_name: SBERT model name for result labeling

    Returns:
        OLSStageResult for Stage 3, beta_pm corresponds to 'tier_rank'
    """
    df2 = df.copy()
    df2['tier_rank'] = df2['tier'].map(TIER_RANK_MAP).astype(float)
    X = sm.add_constant(df2[['tier_rank'] + SURFACE_FEATURE_COLS])
    y = df2['c_sem']
    res = sm.OLS(y, X).fit(cov_type=cov_type)
    logger.debug(f"[Stage3] nobs={int(res.nobs)}, beta_tier_rank={res.params.get('tier_rank', float('nan')):.4f}")
    return _extract_stage_result(res, model_name, 'robustness', pm_col='tier_rank')


def compute_mediation_proportion(
    beta_pm_reduced: float,
    beta_pm_full: float,
) -> Tuple[float, float]:
    """Stage 4: Returns (mediation_ratio, pm_effect_retained).

    mediation_ratio = (beta_pm_reduced - beta_pm_full) / beta_pm_reduced
    pm_effect_retained = |beta_pm_full / beta_pm_reduced|

    Returns (nan, nan) if beta_pm_reduced == 0.

    Args:
        beta_pm_reduced: beta_pm from Stage 1 (PM-only model)
        beta_pm_full: beta_pm from Stage 2 (full model)

    Returns:
        Tuple (mediation_ratio, pm_effect_retained)
    """
    if beta_pm_reduced == 0 or np.isnan(beta_pm_reduced):
        return float('nan'), float('nan')

    mediation_ratio = (beta_pm_reduced - beta_pm_full) / beta_pm_reduced
    pm_effect_retained = abs(beta_pm_full / beta_pm_reduced)
    return float(mediation_ratio), float(pm_effect_retained)


def compute_vif(df: pd.DataFrame, feature_cols: List[str]) -> Dict[str, float]:
    """Compute Variance Inflation Factors for multicollinearity diagnostics.

    Args:
        df: DataFrame containing the feature columns
        feature_cols: List of column names to compute VIF for

    Returns:
        Dict mapping column_name -> VIF value
    """
    vif_data = df[feature_cols].dropna()
    if len(vif_data) == 0:
        return {col: float('nan') for col in feature_cols}

    X = sm.add_constant(vif_data)
    vif_dict = {}
    for i, col in enumerate(feature_cols):
        try:
            vif_val = variance_inflation_factor(X.values, i + 1)  # +1 for const
            vif_dict[col] = float(vif_val)
        except Exception as e:
            logger.warning(f"VIF computation failed for {col}: {e}")
            vif_dict[col] = float('nan')

    return vif_dict


def check_rank_deficiency(df: pd.DataFrame, feature_cols: List[str]) -> bool:
    """Check for matrix rank deficiency before OLS fit.

    Args:
        df: DataFrame containing the feature columns
        feature_cols: List of column names to check

    Returns:
        True if matrix is full rank (safe to fit OLS), False if rank deficient
    """
    data = df[feature_cols].dropna()
    if len(data) == 0:
        return False

    X = sm.add_constant(data).values
    rank = np.linalg.matrix_rank(X)
    expected_rank = X.shape[1]
    return rank == expected_rank


def run_mediation_ols(
    df: pd.DataFrame,
    model_name: str,
    cov_type: str = 'HC3',
) -> MediationResult:
    """Run all 4 stages for one SBERT model's regression DataFrame.

    Args:
        df: Regression DataFrame with columns: tier, pm_proxy, c_sem,
            response_length, bullet_density, politeness_freq, ttr, mean_sent_len
        model_name: SBERT model name for result labeling
        cov_type: Covariance type for robust SE (default 'HC3')

    Returns:
        MediationResult with all 4 stages
    """
    # Rank deficiency check
    check_cols = ['pm_proxy'] + SURFACE_FEATURE_COLS
    if not check_rank_deficiency(df, check_cols):
        logger.error(f"[{model_name}] Rank deficiency detected — OLS may be unreliable")

    # Stage 1: PM-only
    stage1 = run_pm_only_model(df, cov_type=cov_type, model_name=model_name)
    beta_pm_reduced = stage1.beta_pm
    logger.info(f"[{model_name}] Stage1 beta_pm={beta_pm_reduced:.4f}, p={stage1.p_pm:.4f}")

    # Stage 2: Full model
    stage2 = run_full_model(df, cov_type=cov_type, model_name=model_name)
    beta_pm_full = stage2.beta_pm
    logger.info(f"[{model_name}] Stage2 beta_pm={beta_pm_full:.4f}, p={stage2.p_pm:.4f}")

    # Stage 3: Robustness
    stage3 = run_robustness_model(df, cov_type=cov_type, model_name=model_name)
    logger.info(f"[{model_name}] Stage3 beta_tier_rank={stage3.beta_pm:.4f}, p={stage3.p_pm:.4f}")

    # Stage 4: Mediation proportion
    med_ratio, retained = compute_mediation_proportion(beta_pm_reduced, beta_pm_full)
    logger.info(f"[{model_name}] Mediation ratio={med_ratio:.4f}, retained={retained:.4f}")

    # VIF diagnostics
    vif_cols = ['pm_proxy'] + SURFACE_FEATURE_COLS
    vif_results = compute_vif(df, vif_cols)
    for col, vif_val in vif_results.items():
        if not np.isnan(vif_val) and vif_val > 10.0:
            logger.warning(f"[{model_name}] High VIF for {col}: {vif_val:.2f}")

    return MediationResult(
        model_name=model_name,
        beta_pm_reduced=beta_pm_reduced,
        beta_pm_full=beta_pm_full,
        mediation_ratio=med_ratio,
        pm_effect_retained=retained,
        stage_pm_only=stage1,
        stage_full=stage2,
        stage_robustness=stage3,
    )
