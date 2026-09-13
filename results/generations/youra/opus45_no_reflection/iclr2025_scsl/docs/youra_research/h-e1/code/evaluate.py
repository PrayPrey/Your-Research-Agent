import numpy as np
from sklearn.metrics import roc_auc_score, precision_recall_curve


def compute_metrics(cv_values: list, ground_truth_spurious: list) -> dict:
    scores = -np.array(cv_values)

    auc = roc_auc_score(ground_truth_spurious, scores)

    precisions, recalls, thresholds = precision_recall_curve(ground_truth_spurious, scores)
    f1_scores = 2 * (precisions * recalls) / (precisions + recalls + 1e-8)
    best_f1 = float(np.max(f1_scores))

    return {"auc": float(auc), "best_f1": best_f1}


def check_gate(metrics: dict, threshold: float = 0.75) -> bool:
    return metrics["auc"] >= threshold
