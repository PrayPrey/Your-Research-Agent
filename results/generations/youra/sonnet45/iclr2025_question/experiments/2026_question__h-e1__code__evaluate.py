"""Evaluation and variance metrics calculation."""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import numpy as np
from scipy import stats
from typing import Dict, List, Any


def evaluate_model(model: nn.Module, test_loader: DataLoader, device: str) -> float:
    """Compute test accuracy.

    Args:
        model: Neural network model
        test_loader: Test data loader
        device: 'cuda' or 'cpu'

    Returns:
        Test accuracy as percentage (0-100)
    """
    model.eval()
    correct = 0
    total = 0

    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            pred = output.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()
            total += target.size(0)

    accuracy = 100.0 * correct / total
    return accuracy


def compute_variance_metrics(test_accuracies: List[float]) -> Dict[str, float]:
    """Calculate variance, std, CV%, and bootstrap CI.

    Args:
        test_accuracies: List of test accuracy values

    Returns:
        Dictionary with variance metrics:
            - mean: Mean accuracy
            - variance: Sample variance
            - std: Standard deviation
            - cv_percent: Coefficient of variation (%)
            - ci_lower: 95% CI lower bound
            - ci_upper: 95% CI upper bound
    """
    accuracies = np.array(test_accuracies)

    # Basic statistics
    mean_acc = np.mean(accuracies)
    var_acc = np.var(accuracies, ddof=1)  # Sample variance
    std_acc = np.std(accuracies, ddof=1)
    cv_percent = (std_acc / mean_acc) * 100 if mean_acc > 0 else 0

    # Bootstrap confidence interval (10000 resamples)
    n_bootstrap = 10000
    bootstrap_means = []
    n = len(accuracies)

    for _ in range(n_bootstrap):
        resample = np.random.choice(accuracies, size=n, replace=True)
        bootstrap_means.append(np.mean(resample))

    ci_lower = np.percentile(bootstrap_means, 2.5)
    ci_upper = np.percentile(bootstrap_means, 97.5)

    return {
        "mean": float(mean_acc),
        "variance": float(var_acc),
        "std": float(std_acc),
        "cv_percent": float(cv_percent),
        "ci_lower": float(ci_lower),
        "ci_upper": float(ci_upper)
    }


def check_gate_condition(
    variance_summary: Dict[str, Dict[str, float]],
    threshold: float = 0.3
) -> Dict[str, Any]:
    """Validate MUST_WORK gate condition.

    Gate condition: At least 2 out of 4 conditions have variance >= threshold

    Args:
        variance_summary: Variance metrics per condition
        threshold: Variance threshold (default: 0.3%)

    Returns:
        Gate result dictionary with:
            - gate_result: 'PASS' or 'FAIL'
            - conditions_passed: Number of conditions passing threshold
            - total_conditions: Total number of conditions
            - passing_conditions: List of condition names that passed
    """
    passing_conditions = []

    for condition_name, metrics in variance_summary.items():
        if metrics["variance"] >= threshold:
            passing_conditions.append(condition_name)

    conditions_passed = len(passing_conditions)
    total_conditions = len(variance_summary)

    # MUST_WORK gate: >= 2 out of 4 conditions pass threshold
    gate_result = "PASS" if conditions_passed >= 2 else "FAIL"

    return {
        "gate_result": gate_result,
        "gate_type": "MUST_WORK",
        "conditions_passed": conditions_passed,
        "total_conditions": total_conditions,
        "passing_conditions": passing_conditions,
        "threshold": threshold,
        "criterion": "At least 2/4 conditions with variance >= 0.3%"
    }
