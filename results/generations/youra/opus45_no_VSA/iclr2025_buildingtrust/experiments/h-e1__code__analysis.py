"""Analysis: OLS residualization, PCA, permutation test, assumption checks."""
import numpy as np
import statsmodels.api as sm
from sklearn.decomposition import PCA
from scipy.stats import shapiro
from statsmodels.stats.outliers_influence import variance_inflation_factor
from factor_analyzer.factor_analyzer import calculate_kmo


def residualize(Y: np.ndarray, X: np.ndarray) -> tuple:
    """OLS residualize each column of Y on X (with intercept).

    Returns:
        Y_resid: (N, p) residuals
        r_squared: list of R² values per benchmark
    """
    X_design = sm.add_constant(X)
    n_cols = Y.shape[1]
    Y_resid = np.zeros_like(Y)
    r_squared = []

    for i in range(n_cols):
        model = sm.OLS(Y[:, i], X_design).fit()
        Y_resid[:, i] = model.resid
        r_squared.append(float(model.rsquared))

    return Y_resid, r_squared


def fit_pca(Y_resid: np.ndarray) -> dict:
    """Fit full PCA and extract key statistics."""
    n_components = min(Y_resid.shape[1], Y_resid.shape[0])
    pca = PCA(n_components=n_components)
    pca.fit(Y_resid)

    return {
        "eigenvalues": pca.explained_variance_.tolist(),
        "variance_ratio": pca.explained_variance_ratio_.tolist(),
        "loadings_pc1": pca.components_[0, :].tolist(),
        "lambda_1": float(pca.explained_variance_[0]),
        "variance_explained_pc1": float(pca.explained_variance_ratio_[0]),
    }


def permutation_test(Y_resid: np.ndarray, n_perms: int = 1000, seed: int = 42) -> dict:
    """Column-wise permutation test for λ₁ significance."""
    pca_obs = PCA(n_components=1)
    pca_obs.fit(Y_resid)
    lambda_obs = float(pca_obs.explained_variance_[0])

    rng = np.random.default_rng(seed)
    null_dist = np.empty(n_perms)

    for i in range(n_perms):
        Y_perm = Y_resid.copy()
        for j in range(Y_perm.shape[1]):
            Y_perm[:, j] = rng.permutation(Y_perm[:, j])
        pca_null = PCA(n_components=1)
        pca_null.fit(Y_perm)
        null_dist[i] = pca_null.explained_variance_[0]

    p_value = float((np.sum(null_dist >= lambda_obs) + 1) / (n_perms + 1))
    threshold_95 = float(np.percentile(null_dist, 95))

    assert len(null_dist) == n_perms, f"Null dist size mismatch: {len(null_dist)} != {n_perms}"

    return {
        "lambda_obs": lambda_obs,
        "null_dist": null_dist.tolist(),
        "p_value": p_value,
        "threshold_95": threshold_95,
        "hypothesis_passed": p_value < 0.05 and lambda_obs > threshold_95,
    }


def check_assumptions(Y_resid: np.ndarray, X: np.ndarray) -> dict:
    """Run assumption checks: normality, VIF, KMO."""
    results = {}

    # Shapiro-Wilk on first PC scores
    pca = PCA(n_components=1)
    pc1_scores = pca.fit_transform(Y_resid)[:, 0]
    sample_size = min(len(pc1_scores), 5000)
    if sample_size < len(pc1_scores):
        rng = np.random.default_rng(42)
        sample_idx = rng.choice(len(pc1_scores), sample_size, replace=False)
        pc1_sample = pc1_scores[sample_idx]
    else:
        pc1_sample = pc1_scores
    stat, shapiro_p = shapiro(pc1_sample)
    results["shapiro_p"] = float(shapiro_p)
    results["shapiro_stat"] = float(stat)

    # VIF for confounds
    X_design = sm.add_constant(X)
    vif_values = []
    for i in range(X_design.shape[1]):
        vif = variance_inflation_factor(X_design, i)
        vif_values.append(float(vif))
    results["vif"] = vif_values[1:]  # Exclude intercept
    results["vif_max"] = float(max(vif_values[1:]))

    # KMO
    try:
        kmo_all, kmo_model = calculate_kmo(Y_resid)
        results["kmo"] = float(kmo_model)
    except Exception:
        results["kmo"] = None

    return results
