"""Expected Calibration Error (ECE) computation."""
import numpy as np


def compute_ece(predictions, confidences, labels, n_bins=10):
    """
    Compute Expected Calibration Error.

    Args:
        predictions: [N] predicted class labels
        confidences: [N] max softmax probabilities
        labels: [N] ground truth labels
        n_bins: number of confidence bins (default 10)

    Returns:
        ece: float in [0, 1]
    """
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0

    for i in range(n_bins):
        # Find samples in this bin
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]
        in_bin = (confidences > bin_lower) & (confidences <= bin_upper)

        if in_bin.sum() == 0:
            continue  # Skip empty bins

        # Compute accuracy and confidence in this bin
        bin_acc = (predictions[in_bin] == labels[in_bin]).astype(float).mean()
        bin_conf = confidences[in_bin].mean()
        bin_weight = in_bin.sum() / len(labels)

        # Add weighted absolute difference
        ece += bin_weight * abs(bin_acc - bin_conf)

    return ece


def compute_bin_statistics(confidences, correctness, n_bins=10):
    """
    Compute per-bin statistics for reliability diagram.

    Args:
        confidences: [N] confidence scores
        correctness: [N] boolean correctness (1 if correct, 0 otherwise)
        n_bins: number of bins

    Returns:
        bin_centers: [n_bins] center of each bin
        bin_accuracies: [n_bins] accuracy per bin (NaN for empty bins)
        bin_counts: [n_bins] number of samples per bin
    """
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    bin_centers = (bin_boundaries[:-1] + bin_boundaries[1:]) / 2
    bin_accuracies = np.full(n_bins, np.nan)
    bin_counts = np.zeros(n_bins)

    for i in range(n_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]
        in_bin = (confidences > bin_lower) & (confidences <= bin_upper)

        if in_bin.sum() > 0:
            bin_accuracies[i] = correctness[in_bin].mean()
            bin_counts[i] = in_bin.sum()

    return bin_centers, bin_accuracies, bin_counts
