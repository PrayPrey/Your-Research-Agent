"""H-M2: LightGBM 5-fold CV trainer + MSE_perm decomposition."""
import numpy as np
from lightgbm import LGBMRegressor
from sklearn.model_selection import KFold
from sklearn.metrics import mean_squared_error, r2_score
from scipy.stats import kendalltau

LGBM_PARAMS: dict = {
    "n_estimators": 500,
    "learning_rate": 0.05,
    "num_leaves": 31,
    "reg_alpha": 0.0,
    "reg_lambda": 0.1,
    "random_state": 42,
    "boosting_type": "gbdt",
    "verbose": -1,
}


def run_cv_lgbm(
    X: np.ndarray,
    y: np.ndarray,
    n_splits: int = 5,
    random_state: int = 42,
    params: dict = None,
) -> tuple:
    """
    Returns (fold_preds, full_model).
    fold_preds: (N,) OOF predictions on original X
    full_model: LGBMRegressor trained on all N samples
    """
    if params is None:
        params = LGBM_PARAMS.copy()

    N = len(y)
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    fold_preds = np.zeros(N, dtype=np.float64)

    for fold, (train_idx, val_idx) in enumerate(kf.split(X)):
        model = LGBMRegressor(**params)
        model.fit(X[train_idx], y[train_idx])
        fold_preds[val_idx] = model.predict(X[val_idx])
        print(f"  [CV fold {fold+1}/{n_splits}] val MSE={mean_squared_error(y[val_idx], fold_preds[val_idx]):.6f}")

    full_model = LGBMRegressor(**params)
    full_model.fit(X, y)
    print(f"[run_cv_lgbm] Full model trained. OOF MSE={mean_squared_error(y, fold_preds):.6f}")
    return fold_preds, full_model


def compute_orbit_preds(
    full_model,
    permuted_X: np.ndarray,
) -> np.ndarray:
    """
    Returns orbit_preds: (N, K) float64.
    orbit_preds[:, k] = full_model.predict(permuted_X[:, k, :])
    """
    N, K, embed_dim = permuted_X.shape
    orbit_preds = np.zeros((N, K), dtype=np.float64)
    for k in range(K):
        orbit_preds[:, k] = full_model.predict(permuted_X[:, k, :])
    print(f"[compute_orbit_preds] orbit_preds.shape={orbit_preds.shape}")
    return orbit_preds


def decompose_mse(
    y: np.ndarray,
    fold_preds: np.ndarray,
    orbit_preds: np.ndarray,
) -> dict:
    """
    Returns dict with keys:
      mse_total, mse_perm, mse_res, ratio, r2_c1, tau_c1,
      y_avg_pred, r2_c1_avg, tau_c1_avg, per_model_orbit_var, orbit_preds
    """
    y = y.astype(np.float64)
    fold_preds = fold_preds.astype(np.float64)
    orbit_preds = orbit_preds.astype(np.float64)

    mse_total = float(mean_squared_error(y, fold_preds))
    r2_c1 = float(r2_score(y, fold_preds))
    tau_c1 = float(kendalltau(y, fold_preds).statistic)

    # per-model orbit variance: Var_k(ŷ) for each model v
    per_model_orbit_var = np.var(orbit_preds, axis=1, ddof=0)  # (N,), float64

    # MSE_perm = E_v[Var_k(ŷ(π_k · W_v))]
    mse_perm = float(np.mean(per_model_orbit_var))
    mse_res = mse_total - mse_perm
    ratio = mse_perm / mse_total if mse_total > 0 else 0.0

    # orbit-averaged control predictions
    y_avg_pred = orbit_preds.mean(axis=1)  # (N,)
    r2_c1_avg = float(r2_score(y, y_avg_pred))
    tau_c1_avg = float(kendalltau(y, y_avg_pred).statistic)

    print(f"[decompose_mse] MSE_total={mse_total:.6f}  MSE_perm={mse_perm:.6f}  ratio={ratio:.4f}")
    print(f"[decompose_mse] R²(C1)={r2_c1:.4f}  τ(C1)={tau_c1:.4f}")
    print(f"[decompose_mse] R²(C1_avg)={r2_c1_avg:.4f}  τ(C1_avg)={tau_c1_avg:.4f}")

    return {
        "mse_total": mse_total,
        "mse_perm": mse_perm,
        "mse_res": mse_res,
        "ratio": ratio,
        "r2_c1": r2_c1,
        "tau_c1": tau_c1,
        "y_avg_pred": y_avg_pred,
        "r2_c1_avg": r2_c1_avg,
        "tau_c1_avg": tau_c1_avg,
        "per_model_orbit_var": per_model_orbit_var,
        "orbit_preds": orbit_preds,
    }
