"""Evaluation utilities: per-domain analysis and coverage verification."""

import numpy as np
import logging
from uncertainty import _compute_metrics

logger = logging.getLogger(__name__)


def evaluate_per_domain(test_results, predictions):
    """Evaluate metrics broken down by domain."""
    domains = list(set(r["domain"] for r in test_results))
    domain_metrics = {}

    for domain in domains:
        mask = [r["domain"] == domain for r in test_results]
        domain_results = [r for r, m in zip(test_results, mask) if m]
        domain_preds = [p for p, m in zip(predictions, mask) if m]

        if not domain_results:
            continue

        y_true = np.array([1 - r["correct"] for r in domain_results])
        y_pred = np.array([p["predicted_hallucination"] for p in domain_preds])
        scores = np.array([p["nonconformity_score"] for p in domain_preds])

        metrics = _compute_metrics(y_true, y_pred, scores)
        domain_metrics[domain] = metrics
        logger.info(f"  Domain '{domain}': AUROC={metrics['auroc']:.3f}, F1={metrics['f1']:.3f}")

    return domain_metrics


def evaluate_coverage_by_alpha(cal_results, test_results, model_instance, alphas=None):
    """
    Evaluate empirical coverage for different alpha values.
    Returns list of (alpha, theoretical_coverage, empirical_coverage) tuples.
    """
    if alphas is None:
        alphas = [0.01, 0.05, 0.10, 0.15, 0.20, 0.25]

    coverage_data = []
    from uncertainty import HalluConform
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import LogisticRegression

    for alpha in alphas:
        hc = HalluConform(alpha=alpha, use_adaptive=False)
        hc.calibrate(cal_results)
        metrics, preds = hc.evaluate(test_results, use_domain_risk=False)
        coverage_data.append({
            "alpha": alpha,
            "theoretical_coverage": 1 - alpha,
            "empirical_coverage": metrics["empirical_coverage"],
        })
        logger.info(
            f"  alpha={alpha:.2f}: theoretical={1-alpha:.2f}, "
            f"empirical={metrics['empirical_coverage']:.3f}"
        )

    return coverage_data


def compute_signal_importance(model_instance):
    """Return the learned signal weights from the logistic regression."""
    if not model_instance.is_fitted:
        return {}
    weights = model_instance.weights_
    signal_names = ["token_entropy", "attention_consistency", "hidden_divergence"]
    return {name: float(w) for name, w in zip(signal_names, weights)}
