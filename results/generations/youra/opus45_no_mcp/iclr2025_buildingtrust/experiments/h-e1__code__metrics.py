"""ECE computation and metrics."""
import numpy as np
from config import CONFIG


def compute_ece(confidences: np.ndarray, accuracies: np.ndarray, n_bins: int = None) -> float:
    """Compute Expected Calibration Error with equal-width bins."""
    if n_bins is None:
        n_bins = CONFIG.experiment.n_bins

    if len(confidences) == 0:
        return None

    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0

    for i in range(n_bins):
        if i == 0:
            in_bin = (confidences >= bin_boundaries[i]) & (confidences <= bin_boundaries[i + 1])
        else:
            in_bin = (confidences > bin_boundaries[i]) & (confidences <= bin_boundaries[i + 1])

        prop_in_bin = in_bin.mean()
        if prop_in_bin > 0:
            avg_conf = confidences[in_bin].mean()
            avg_acc = accuracies[in_bin].mean()
            ece += np.abs(avg_acc - avg_conf) * prop_in_bin

    return float(ece)


def extraction_rate(n_success: int, n_total: int) -> float:
    """Compute extraction success rate."""
    if n_total == 0:
        return 0.0
    return n_success / n_total
