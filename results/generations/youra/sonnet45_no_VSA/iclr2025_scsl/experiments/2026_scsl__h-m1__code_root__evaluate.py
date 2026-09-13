"""Evaluation metrics and statistical analysis"""
import numpy as np
from typing import Dict, List
from scipy.stats import spearmanr
import torch
import torch.nn as nn
from torch.utils.data import DataLoader


def compute_asymmetric_accuracy(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    asymmetric_digits: List[int] = [2, 3, 5, 6, 7, 9]
) -> float:
    """Compute accuracy on asymmetric digit subset.

    Args:
        y_true: Ground truth labels [N]
        y_pred: Predicted labels [N]
        asymmetric_digits: List of asymmetric digit classes

    Returns:
        accuracy: float (0.0-1.0)
    """
    mask = np.isin(y_true, asymmetric_digits)
    if mask.sum() == 0:
        return 0.0
    return (y_true[mask] == y_pred[mask]).mean()


def compute_per_digit_accuracy(
    y_true: np.ndarray,
    y_pred: np.ndarray
) -> Dict[int, float]:
    """Compute accuracy per digit class.

    Args:
        y_true: Ground truth labels [N]
        y_pred: Predicted labels [N]

    Returns:
        {0: acc0, 1: acc1, ..., 9: acc9}
    """
    per_digit_acc = {}
    for digit in range(10):
        mask = (y_true == digit)
        if mask.sum() > 0:
            per_digit_acc[digit] = (y_true[mask] == y_pred[mask]).mean()
        else:
            per_digit_acc[digit] = 0.0
    return per_digit_acc


def evaluate_model(
    model: nn.Module,
    dataloader: DataLoader,
    device: str,
    asymmetric_digits: List[int] = [2, 3, 5, 6, 7, 9]
) -> Dict:
    """Evaluate model on test set.

    Args:
        model: Trained CNN
        dataloader: Test DataLoader (no augmentation)
        device: "cuda" or "cpu"
        asymmetric_digits: List of asymmetric digits

    Returns:
        results dict with all metrics
    """
    model.eval()
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for images, labels in dataloader:
            images = images.to(device)
            logits = model(images)  # [B, 10]
            preds = logits.argmax(dim=1)  # [B]
            all_preds.append(preds.cpu())
            all_labels.append(labels.cpu())

    y_pred = torch.cat(all_preds).numpy()
    y_true = torch.cat(all_labels).numpy()

    overall_acc = (y_true == y_pred).mean()
    asymmetric_acc = compute_asymmetric_accuracy(y_true, y_pred, asymmetric_digits)
    per_digit_acc = compute_per_digit_accuracy(y_true, y_pred)

    return {
        "overall_accuracy": float(overall_acc),
        "asymmetric_accuracy": float(asymmetric_acc),
        "per_digit_accuracy": per_digit_acc,
        "y_true": y_true,
        "y_pred": y_pred
    }


def dose_response_test(
    results: Dict[float, List[float]],
    alpha: float = 0.05
) -> Dict:
    """Test dose-response relationship (Spearman correlation).

    Args:
        results: {flip_prob: [acc_seed1, acc_seed2, ...], ...}
        alpha: Significance level

    Returns:
        test results including gate status
    """
    flip_probs = sorted(results.keys())
    mean_accs = [np.mean(results[p]) for p in flip_probs]

    rho, p_value = spearmanr(flip_probs, mean_accs)

    # Gate: rho < 0 AND p < alpha
    gate_status = "PASS" if (rho < 0 and p_value < alpha) else "FAIL"

    return {
        "spearman_rho": float(rho),
        "spearman_p": float(p_value),
        "gate_status": gate_status,
        "mean_accs": mean_accs,
        "flip_probs": flip_probs
    }
