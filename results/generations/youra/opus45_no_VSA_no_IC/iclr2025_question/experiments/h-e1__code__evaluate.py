"""Evaluation metrics and success criteria."""

from sklearn.metrics import roc_auc_score


def compute_auroc(y_true: list, y_pred_proba) -> float:
    """Compute AUROC."""
    if len(set(y_true)) < 2:
        return 0.5
    return roc_auc_score(y_true, y_pred_proba)


def compute_gap(auroc_sep: float, auroc_se: float) -> float:
    """Compute gap between SEP and SE AUROC."""
    return auroc_se - auroc_sep


def check_success(gaps: dict) -> dict:
    """Check if hypothesis criteria met: gap <= 0.05 for >= 2/3 models, all <= 0.10."""
    n_models = len(gaps)
    n_within_05 = sum(1 for g in gaps.values() if g <= 0.05)
    all_within_10 = all(g <= 0.10 for g in gaps.values())
    ratio_within_05 = n_within_05 / n_models if n_models > 0 else 0
    passed = ratio_within_05 >= 2/3 and all_within_10
    return {
        "passed": passed,
        "n_models": n_models,
        "n_within_05": n_within_05,
        "ratio_within_05": ratio_within_05,
        "all_within_10": all_within_10,
        "gaps": gaps,
    }
