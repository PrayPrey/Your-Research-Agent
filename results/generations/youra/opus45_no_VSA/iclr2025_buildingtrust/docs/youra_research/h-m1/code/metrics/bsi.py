"""Behavioral Stability Index (BSI) computation."""

import numpy as np


def compute_bsi(paws_acc: float, qqp_acc: float) -> float:
    """
    Compute Behavioral Stability Index as geometric mean.

    Args:
        paws_acc: Accuracy on PAWS test set [0, 1]
        qqp_acc: Accuracy on QQP validation set [0, 1]

    Returns:
        bsi: Geometric mean of accuracies
    """
    paws_acc = max(0.0, min(1.0, paws_acc))
    qqp_acc = max(0.0, min(1.0, qqp_acc))
    return float(np.sqrt(paws_acc * qqp_acc))
