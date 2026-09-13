# evaluate.py - AUROC/AUPRC computation and gate check
from sklearn.metrics import roc_auc_score, average_precision_score
from config import AUROC_THRESHOLD


def compute_metrics(y_true: list[int], scores: dict[str, list[float]]) -> dict:
    """Compute AUROC and AUPRC for each UQ method."""
    metrics = {}
    for method, method_scores in scores.items():
        try:
            auroc = roc_auc_score(y_true, method_scores)
            auprc = average_precision_score(y_true, method_scores)
        except ValueError:
            auroc = 0.5
            auprc = sum(y_true) / len(y_true) if y_true else 0.5
        metrics[method] = {"auroc": auroc, "auprc": auprc}
    return metrics


def apply_gate(metrics: dict, threshold: float = AUROC_THRESHOLD) -> tuple[bool, str]:
    """Check if any method passes AUROC threshold. Returns (passed, best_method)."""
    best_method = max(metrics.keys(), key=lambda m: metrics[m]["auroc"])
    best_auroc = metrics[best_method]["auroc"]
    passed = best_auroc > threshold
    return passed, best_method


if __name__ == "__main__":
    # Demo
    y_true = [0, 1, 1, 0, 1, 0, 0, 1]
    scores = {
        "token_entropy": [0.2, 0.8, 0.7, 0.3, 0.9, 0.1, 0.4, 0.6],
        "semantic_entropy": [0.3, 0.7, 0.8, 0.2, 0.85, 0.15, 0.35, 0.65],
    }
    metrics = compute_metrics(y_true, scores)
    print(f"Metrics: {metrics}")
    passed, best = apply_gate(metrics)
    print(f"Gate passed: {passed}, Best method: {best}")
