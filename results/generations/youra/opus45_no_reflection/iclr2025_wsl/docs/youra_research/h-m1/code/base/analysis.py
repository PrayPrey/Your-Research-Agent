"""Analysis module for H-E1 experiment."""

import numpy as np
from sklearn.metrics import r2_score


def compute_class_wise_accuracy(
    predictions: dict,
    ground_truth: np.ndarray,
    n_classes: int
) -> tuple:
    """Compute class-wise accuracy for each model.

    Args:
        predictions: {model_id: preds}, preds shape (10000,)
        ground_truth: shape (10000,)
        n_classes: number of classes (10 for CIFAR-10)

    Returns:
        class_wise_acc: shape (N, 10) accuracy per class per model
        overall_acc: shape (N,) overall accuracy per model
        model_ids: list of model IDs in order
    """
    model_ids = list(predictions.keys())
    n_models = len(model_ids)

    class_wise_acc = np.zeros((n_models, n_classes))
    overall_acc = np.zeros(n_models)

    for i, model_id in enumerate(model_ids):
        pred = predictions[model_id]
        overall_acc[i] = (pred == ground_truth).mean()

        for c in range(n_classes):
            mask = ground_truth == c
            if mask.sum() > 0:
                class_wise_acc[i, c] = (pred[mask] == c).mean()

    return class_wise_acc, overall_acc, model_ids


def stratified_baseline(
    class_wise_acc: np.ndarray,
    overall_acc: np.ndarray
) -> tuple:
    """Compute stratified baseline prediction.

    Formula: baseline_pred[i,c] = overall_acc[i] * class_difficulty[c] / mean(class_difficulty)

    Args:
        class_wise_acc: shape (N, 10)
        overall_acc: shape (N,)

    Returns:
        baseline_pred: shape (N, 10)
        class_difficulty: shape (10,)
    """
    class_difficulty = class_wise_acc.mean(axis=0)  # (10,)
    mean_difficulty = class_difficulty.mean()

    # Avoid division by zero
    if mean_difficulty == 0:
        baseline_pred = np.zeros_like(class_wise_acc)
    else:
        baseline_pred = overall_acc[:, None] * class_difficulty[None, :] / mean_difficulty

    assert baseline_pred.shape == class_wise_acc.shape, "Shape mismatch"

    return baseline_pred, class_difficulty


def variance_analysis(
    class_wise_acc: np.ndarray,
    baseline_pred: np.ndarray
) -> dict:
    """Compute variance decomposition.

    Returns:
        dict with total_variance, residual_variance, residual_ratio, r2_baseline
    """
    total_variance = np.var(class_wise_acc)

    # Guard divide-by-zero
    if total_variance == 0:
        return {
            "total_variance": 0.0,
            "residual_variance": 0.0,
            "residual_ratio": 0.0,
            "r2_baseline": 1.0
        }

    residual = class_wise_acc - baseline_pred
    residual_variance = np.var(residual)
    residual_ratio = residual_variance / total_variance
    r2_baseline = r2_score(class_wise_acc.ravel(), baseline_pred.ravel())

    return {
        "total_variance": float(total_variance),
        "residual_variance": float(residual_variance),
        "residual_ratio": float(residual_ratio),
        "r2_baseline": float(r2_baseline)
    }


def per_class_variance(class_wise_acc: np.ndarray) -> np.ndarray:
    """Compute variance per class across models.

    Args:
        class_wise_acc: shape (N, 10)

    Returns:
        shape (10,) variance per class
    """
    return class_wise_acc.var(axis=0)
