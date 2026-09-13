import numpy as np
from scipy.signal import correlate, correlation_lags
from typing import Tuple, List

def compute_lagged_cross_correlation(
    r_series: np.ndarray,
    sr_series: np.ndarray,
    max_lag: int = 5,
) -> Tuple[int, np.ndarray, np.ndarray]:
    r_decay = -np.diff(r_series)
    sr_rise = np.diff(sr_series)
    r_norm = (r_decay - r_decay.mean()) / (r_decay.std() + 1e-8)
    sr_norm = (sr_rise - sr_rise.mean()) / (sr_rise.std() + 1e-8)
    corr = correlate(sr_norm, r_norm, mode='full') / len(r_norm)
    lags = correlation_lags(len(sr_norm), len(r_norm), mode='full')
    valid = (lags >= -max_lag) & (lags <= max_lag)
    valid_corr = corr[valid]
    valid_lags = lags[valid]
    tau = valid_lags[np.argmax(valid_corr)]
    return int(tau), valid_corr, valid_lags

def bootstrap_ci_tau(
    tau_per_seed: List[int],
    confidence: float = 0.95,
    n_bootstrap: int = 10000,
) -> Tuple[float, float, float]:
    tau_arr = np.array(tau_per_seed)
    n = len(tau_arr)
    boot_means = np.array([np.mean(np.random.choice(tau_arr, size=n, replace=True)) for _ in range(n_bootstrap)])
    mean_tau = np.mean(tau_arr)
    alpha = 1 - confidence
    ci_low = np.percentile(boot_means, 100 * alpha / 2)
    ci_high = np.percentile(boot_means, 100 * (1 - alpha / 2))
    return mean_tau, ci_low, ci_high
