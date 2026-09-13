"""Peak detection and statistical tests."""
import numpy as np
from scipy.stats import wilcoxon

def find_peak_epoch(accuracies, window=5):
    """Find peak epoch with smoothing."""
    acc_array = np.array(accuracies)
    kernel = np.ones(window) / window
    smoothed = np.convolve(acc_array, kernel, mode="valid")
    peak_idx = np.argmax(smoothed)
    peak_epoch = peak_idx + window // 2 + 1  # 1-based
    return peak_epoch

def compute_auc(accuracies, start=1, end=20):
    """Compute AUC for epoch range."""
    return np.trapezoid(accuracies[start-1:end])

def wilcoxon_test(spurious_acc, core_acc):
    """Wilcoxon signed-rank test on accuracy curves."""
    stat, p = wilcoxon(spurious_acc, core_acc)
    return {"statistic": float(stat), "p_value": float(p)}
