"""Statistical tests for H-M4 SNR comparison."""
import numpy as np
from typing import List, Tuple
from snr_analysis import SNRResult


def bootstrap_snr_ci(
    signals: List[float],
    noises: List[float],
    n_boot: int = 1000,
    alpha: float = 0.05,
    seed: int = 42
) -> Tuple[float, float, List[float]]:
    """Bootstrap 95% CI for SNR. Returns (lower, upper, bootstrap_samples)."""
    rng = np.random.default_rng(seed)
    signals = np.array(signals)
    noises = np.array(noises)
    n = len(signals)

    snrs = []
    for _ in range(n_boot):
        idx = rng.choice(n, size=n, replace=True)
        s = np.mean(signals[idx])
        noise = np.mean(noises[idx]) + 1e-8
        snrs.append(s / noise)

    lower = float(np.percentile(snrs, alpha / 2 * 100))
    upper = float(np.percentile(snrs, (1 - alpha / 2) * 100))
    return lower, upper, snrs


def permutation_test(
    snr_gated: SNRResult,
    snr_always: SNRResult,
    n_perm: int = 9999,
    seed: int = 42
) -> float:
    """Permutation test for SNR difference. Returns p-value."""
    rng = np.random.default_rng(seed)

    observed_diff = snr_gated.snr - snr_always.snr

    combined_signals = np.array(snr_gated.signals + snr_always.signals)
    combined_noises = np.array(snr_gated.noises + snr_always.noises)
    n_gated = len(snr_gated.signals)
    n_total = len(combined_signals)

    count = 0
    for _ in range(n_perm):
        perm = rng.permutation(n_total)
        idx1 = perm[:n_gated]
        idx2 = perm[n_gated:]

        s1 = np.mean(combined_signals[idx1]) / (np.mean(combined_noises[idx1]) + 1e-8)
        s2 = np.mean(combined_signals[idx2]) / (np.mean(combined_noises[idx2]) + 1e-8)

        if abs(s1 - s2) >= abs(observed_diff):
            count += 1

    return (count + 1) / (n_perm + 1)


def compute_improvement(snr_gated: float, snr_always: float) -> float:
    """Percentage improvement: (gated - always) / always * 100."""
    if abs(snr_always) < 1e-8:
        return 0.0
    return (snr_gated - snr_always) / snr_always * 100
