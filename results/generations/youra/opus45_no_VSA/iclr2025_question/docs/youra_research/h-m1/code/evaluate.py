# evaluate.py - h-m1 MECHANISM: Null vs Full model comparison with LRT
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, roc_curve
from scipy.stats import chi2, combine_pvalues
from sklearn.model_selection import StratifiedKFold
from config import CONFIG


def build_feature_matrices(h_l: np.ndarray, nti: np.ndarray, cmi: np.ndarray):
    """Build null (H_L only) and full (H_L + NTI + CMI) feature matrices."""
    # Handle NaN/Inf in features
    h_l = np.nan_to_num(h_l, nan=0.0, posinf=0.0, neginf=0.0)
    nti = np.nan_to_num(nti, nan=0.0, posinf=0.0, neginf=0.0)
    cmi = np.nan_to_num(cmi, nan=0.0, posinf=0.0, neginf=0.0)

    X_null = h_l.reshape(-1, 1)  # [N, 1]
    X_full = np.column_stack([h_l, nti, cmi])  # [N, 3]
    return X_null, X_full


def fit_and_compare(X_null_train, X_null_test, X_full_train, X_full_test,
                    y_train, y_test, C=None, max_iter=None):
    """
    Fit null and full logistic regression models, compute AUROC and LRT.

    Returns dict with metrics for this fold.
    """
    C = C or CONFIG["logreg_C"]
    max_iter = max_iter or CONFIG["logreg_max_iter"]

    # Fit null model (H_L only)
    clf_null = LogisticRegression(C=C, max_iter=max_iter, solver="lbfgs")
    clf_null.fit(X_null_train, y_train)
    prob_null = clf_null.predict_proba(X_null_test)[:, 1]
    auroc_null = roc_auc_score(y_test, prob_null)

    # ROC curve for null model
    fpr_null, tpr_null, _ = roc_curve(y_test, prob_null)

    # Fit full model (H_L + NTI + CMI)
    clf_full = LogisticRegression(C=C, max_iter=max_iter, solver="lbfgs")
    clf_full.fit(X_full_train, y_train)
    prob_full = clf_full.predict_proba(X_full_test)[:, 1]
    auroc_full = roc_auc_score(y_test, prob_full)

    # ROC curve for full model
    fpr_full, tpr_full, _ = roc_curve(y_test, prob_full)

    # Log-likelihoods for LRT
    eps = 1e-10
    ll_null = np.sum(y_test * np.log(prob_null + eps) +
                     (1 - y_test) * np.log(1 - prob_null + eps))
    ll_full = np.sum(y_test * np.log(prob_full + eps) +
                     (1 - y_test) * np.log(1 - prob_full + eps))

    # LRT statistic and p-value
    G = 2 * (ll_full - ll_null)
    G = max(G, 0)  # G should be non-negative
    p_value = chi2.sf(G, df=CONFIG["lrt_df"])

    return {
        "auroc_null": auroc_null,
        "auroc_full": auroc_full,
        "auroc_gain": auroc_full - auroc_null,
        "ll_null": ll_null,
        "ll_full": ll_full,
        "G": G,
        "p_value": p_value,
        "coef_null": clf_null.coef_[0].tolist(),
        "coef_full": clf_full.coef_[0].tolist(),
        "prob_null": prob_null,
        "prob_full": prob_full,
        "y_test": y_test,
        "roc_null": (fpr_null, tpr_null),
        "roc_full": (fpr_full, tpr_full),
    }


def run_cv_lrt(X_null, X_full, y, n_folds=None, seed=None):
    """
    Run stratified K-fold CV, compute LRT per fold, aggregate results.

    Returns dict with fold results, mean metrics, and combined p-value.
    """
    n_folds = n_folds or CONFIG["n_folds"]
    seed = seed or CONFIG["seed"]

    skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=seed)
    fold_results = []

    for fold_idx, (train_idx, test_idx) in enumerate(skf.split(X_null, y)):
        result = fit_and_compare(
            X_null_train=X_null[train_idx],
            X_null_test=X_null[test_idx],
            X_full_train=X_full[train_idx],
            X_full_test=X_full[test_idx],
            y_train=y[train_idx],
            y_test=y[test_idx],
        )
        result["fold"] = fold_idx
        fold_results.append(result)

    # Aggregate metrics
    auroc_gains = [r["auroc_gain"] for r in fold_results]
    p_values = [r["p_value"] for r in fold_results]

    mean_auroc_gain = np.mean(auroc_gains)
    std_auroc_gain = np.std(auroc_gains)
    mean_auroc_null = np.mean([r["auroc_null"] for r in fold_results])
    mean_auroc_full = np.mean([r["auroc_full"] for r in fold_results])

    # Combined p-value via Fisher's method
    _, combined_p = combine_pvalues(p_values, method="fisher")

    return {
        "fold_results": fold_results,
        "mean_auroc_gain": mean_auroc_gain,
        "std_auroc_gain": std_auroc_gain,
        "mean_auroc_null": mean_auroc_null,
        "mean_auroc_full": mean_auroc_full,
        "combined_p_value": combined_p,
        "n_folds": n_folds,
    }


def check_gate(cv_results: dict, config: dict = None) -> tuple:
    """
    Check if results pass the MECHANISM gate.

    Returns (passed: bool, reason: str, verdict: str)
    verdict is "PASS", "FAIL", or "FALSIFIED"
    """
    config = config or CONFIG
    gain = cv_results["mean_auroc_gain"]
    p_val = cv_results["combined_p_value"]

    gain_thresh = config["auroc_gain_threshold"]
    p_thresh = config["lrt_pvalue_threshold"]
    falsify_gain = config["falsify_gain"]
    falsify_p = config["falsify_pvalue"]

    # Check success criteria
    if gain >= gain_thresh and p_val < p_thresh:
        return (True, f"AUROC gain {gain:.4f} >= {gain_thresh}, p={p_val:.4f} < {p_thresh}", "PASS")

    # Check falsification criteria
    if gain < falsify_gain or p_val >= falsify_p:
        reason = []
        if gain < falsify_gain:
            reason.append(f"gain {gain:.4f} < {falsify_gain}")
        if p_val >= falsify_p:
            reason.append(f"p={p_val:.4f} >= {falsify_p}")
        return (False, "FALSIFIED: " + ", ".join(reason), "FALSIFIED")

    # Inconclusive
    return (False, f"Inconclusive: gain={gain:.4f}, p={p_val:.4f}", "INCONCLUSIVE")
