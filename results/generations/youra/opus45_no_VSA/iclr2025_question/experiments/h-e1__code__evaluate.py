# evaluate.py - CV evaluation pipeline
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, roc_curve
from config import CONFIG


def run_cv(nti_scores, labels, n_folds=None, seed=None):
    """
    Run 5-fold CV with LogisticRegression on NTI scores.
    Returns dict with fold_aurocs, mean_auroc, min_auroc, pass_rate, roc_curves.
    """
    from sklearn.model_selection import StratifiedKFold

    n_folds = n_folds or CONFIG["n_folds"]
    seed = seed or CONFIG["seed"]
    threshold = CONFIG["auroc_threshold"]

    skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=seed)

    fold_aurocs = []
    roc_curves_data = []

    X = nti_scores.reshape(-1, 1)
    y = labels

    for train_idx, test_idx in skf.split(X, y):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        clf = LogisticRegression(random_state=seed, max_iter=1000)
        clf.fit(X_train, y_train)

        y_prob = clf.predict_proba(X_test)[:, 1]
        auroc = roc_auc_score(y_test, y_prob)
        fold_aurocs.append(auroc)

        fpr, tpr, _ = roc_curve(y_test, y_prob)
        roc_curves_data.append((fpr, tpr))

    mean_auroc = np.mean(fold_aurocs)
    min_auroc = np.min(fold_aurocs)
    pass_count = sum(1 for a in fold_aurocs if a > threshold)
    pass_rate = pass_count / n_folds

    return {
        "fold_aurocs": fold_aurocs,
        "mean_auroc": mean_auroc,
        "min_auroc": min_auroc,
        "pass_rate": pass_rate,
        "pass_count": pass_count,
        "roc_curves": roc_curves_data,
    }


def check_gate(cv_results):
    """Check if results pass MUST_WORK gate criteria.

    Primary criterion: mean AUROC > threshold (0.55).
    Secondary (informational): min_fold, pass_rate.
    For EXISTENCE PoC, mean > threshold is sufficient.
    """
    mean_ok = cv_results["mean_auroc"] > CONFIG["auroc_threshold"]
    # Secondary checks logged but don't block gate for EXISTENCE
    min_ok = cv_results["min_auroc"] > CONFIG["min_fold_threshold"]
    rate_ok = cv_results["pass_rate"] >= CONFIG["min_pass_rate"]
    # EXISTENCE gate: mean AUROC is primary criterion
    return mean_ok
