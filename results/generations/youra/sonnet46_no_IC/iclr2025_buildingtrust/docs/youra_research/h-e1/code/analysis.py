"""
Analysis module for H-E1: Partial Spearman correlation matrix.
"""

from dataclasses import dataclass
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from scipy.stats import spearmanr, t as t_dist


@dataclass
class AnalysisConfig:
    alpha: float = 0.05
    bonferroni_alpha: float = 0.0033  # 0.05 / 15 pairs
    n_pairs: int = 15
    rho_threshold: float = 0.5
    n_covariates: int = 2             # log10_params, is_RLHF
    df_residual: int = 12             # n - 2 - k = 16 - 2 - 2
    silhouette_threshold: float = 0.3


def raw_spearman_matrix(scores_df: pd.DataFrame) -> tuple:
    """Baseline uncontrolled Spearman. Returns (rho_6x6, pval_6x6)."""
    dims = scores_df.columns.tolist()
    n = len(dims)
    rho = np.eye(n)
    pval = np.zeros((n, n))

    for i in range(n):
        for j in range(i + 1, n):
            r, p = spearmanr(scores_df.iloc[:, i], scores_df.iloc[:, j])
            rho[i, j] = rho[j, i] = r
            pval[i, j] = pval[j, i] = p

    return rho, pval


def ols_residualize(scores_df: pd.DataFrame, covariates_df: pd.DataFrame) -> pd.DataFrame:
    """OLS-residualize each dimension on covariates. Returns [n, 6] residuals."""
    X = covariates_df.values
    residuals = {}
    for col in scores_df.columns:
        y = scores_df[col].values
        reg = LinearRegression().fit(X, y)
        residuals[col] = y - reg.predict(X)
    return pd.DataFrame(residuals, index=scores_df.index)


def _partial_spearman_tstat(rho: float, n: int, k: int) -> tuple:
    """t-stat and two-sided p-value for partial Spearman. df = n - 2 - k."""
    df = n - 2 - k
    denom = max(1 - rho ** 2, 1e-10)
    t = rho * np.sqrt(df / denom)
    p = 2 * t_dist.sf(abs(t), df=df)
    return float(t), float(p)


def partial_spearman_matrix(
    scores_df: pd.DataFrame,
    covariates_df: pd.DataFrame,
    alpha_bonferroni: float = 0.0033,
) -> tuple:
    """Returns (rho_partial [6,6], pval [6,6], significant_pairs).

    significant_pairs: [(dim_i, dim_j, rho, pval), ...] where |rho|>0.5 AND p<alpha
    """
    cfg = AnalysisConfig()
    dims = scores_df.columns.tolist()
    n = len(scores_df)
    k = covariates_df.shape[1]
    ndim = len(dims)

    residuals = ols_residualize(scores_df, covariates_df)

    rho_matrix = np.eye(ndim)
    pval_matrix = np.zeros((ndim, ndim))
    significant_pairs = []

    for i in range(ndim):
        for j in range(i + 1, ndim):
            r, _ = spearmanr(residuals.iloc[:, i], residuals.iloc[:, j])
            _, p = _partial_spearman_tstat(r, n, k)
            rho_matrix[i, j] = rho_matrix[j, i] = r
            pval_matrix[i, j] = pval_matrix[j, i] = p
            if abs(r) > cfg.rho_threshold and p < alpha_bonferroni:
                significant_pairs.append((dims[i], dims[j], float(r), float(p)))

    return rho_matrix, pval_matrix, significant_pairs


def partial_pearson_matrix(
    scores_df: pd.DataFrame,
    covariates_df: pd.DataFrame,
) -> np.ndarray:
    """Sensitivity check: Pearson partial correlation (residuals then corrcoef)."""
    residuals = ols_residualize(scores_df, covariates_df)
    return np.corrcoef(residuals.values.T)


def check_sign_divergence(rho_spearman: np.ndarray, rho_pearson: np.ndarray) -> list:
    """Return list of (i, j) upper-triangle pairs where Spearman and Pearson signs differ."""
    n = rho_spearman.shape[0]
    divergent = []
    for i in range(n):
        for j in range(i + 1, n):
            if np.sign(rho_spearman[i, j]) != np.sign(rho_pearson[i, j]):
                divergent.append((i, j))
    return divergent
