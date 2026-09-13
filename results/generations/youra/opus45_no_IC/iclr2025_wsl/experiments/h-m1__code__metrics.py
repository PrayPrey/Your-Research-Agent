"""Invariance metrics for H-M1."""

import torch
from typing import Dict, List


def compute_invariance_metrics(predictions: List[float]) -> Dict[str, float]:
    """Compute mean, std, max_deviation, invariance_score, invariance_correlation."""
    preds = torch.tensor(predictions)
    mean_pred = preds.mean()
    std_pred = preds.std()
    max_dev = (preds - mean_pred).abs().max()

    invariance_score = 1.0 if max_dev < 1e-5 else 0.0
    invariance_correlation = 1.0 - min(max_dev.item() / (mean_pred.abs().item() + 1e-12), 1.0)

    return {
        "mean": mean_pred.item(),
        "std": std_pred.item(),
        "max_deviation": max_dev.item(),
        "invariance_score": invariance_score,
        "invariance_correlation": invariance_correlation,
    }


def gate_passed(
    metrics: Dict[str, float],
    dev_threshold: float = 1e-5,
    corr_threshold: float = 0.99
) -> bool:
    """MUST_WORK gate: max_deviation < threshold OR correlation > 0.99."""
    return metrics["max_deviation"] < dev_threshold or metrics["invariance_correlation"] > corr_threshold
