import numpy as np


def compute_ece(confidences: np.ndarray, correct: np.ndarray, n_bins: int = 15) -> float:
    bins = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    n = len(confidences)
    for b in range(n_bins):
        if b == n_bins - 1:
            mask = (confidences >= bins[b]) & (confidences <= bins[b + 1])
        else:
            mask = (confidences > bins[b]) & (confidences <= bins[b + 1])
        if mask.sum() == 0:
            continue
        acc_b = correct[mask].mean()
        conf_b = confidences[mask].mean()
        ece += (mask.sum() / n) * abs(acc_b - conf_b)
    return float(ece)


def compute_both(confidences: np.ndarray, correct: np.ndarray):
    return compute_ece(confidences, correct, 15), compute_ece(confidences, correct, 10)
