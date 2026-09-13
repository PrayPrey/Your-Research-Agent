import numpy as np
from sklearn.metrics import roc_auc_score

def compute_auroc(y_true: np.ndarray, scores: np.ndarray, n_bootstrap: int = 1000) -> tuple[float, float, float]:
    auroc = roc_auc_score(y_true, scores)
    rng = np.random.default_rng(42)
    bootstrap_aurocs = []
    n = len(y_true)
    for _ in range(n_bootstrap):
        idx = rng.choice(n, size=n, replace=True)
        if len(np.unique(y_true[idx])) < 2:
            continue
        bootstrap_aurocs.append(roc_auc_score(y_true[idx], scores[idx]))
    if len(bootstrap_aurocs) < 10:
        return auroc, auroc, auroc
    ci_low = np.percentile(bootstrap_aurocs, 2.5)
    ci_high = np.percentile(bootstrap_aurocs, 97.5)
    return auroc, ci_low, ci_high

def check_gate(results: dict, threshold: float = 0.55) -> bool:
    for dataset_name, methods in results.items():
        for method_name, metrics in methods.items():
            if metrics["auroc"] <= threshold:
                return False
    return True
