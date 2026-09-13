import numpy as np
from scipy import stats
from typing import Dict, Any, List


def compute_mean_spatial_frequency(patch: np.ndarray) -> float:
    if patch.ndim == 3:
        gray = (0.299 * patch[:, :, 0] + 0.587 * patch[:, :, 1] + 0.114 * patch[:, :, 2]).astype(float)
    else:
        gray = patch.astype(float)

    F = np.fft.fft2(gray)
    F_shift = np.fft.fftshift(F)
    power = np.abs(F_shift) ** 2

    H, W = gray.shape
    freq_y = np.fft.fftshift(np.fft.fftfreq(H))
    freq_x = np.fft.fftshift(np.fft.fftfreq(W))
    freq_grid = np.sqrt(freq_y[:, None] ** 2 + freq_x[None, :] ** 2)

    mean_freq = (power * freq_grid).sum() / (power.sum() + 1e-10)
    return float(mean_freq)


def compute_fft_metric(
    spurious_patches: np.ndarray,
    core_patches: np.ndarray,
) -> Dict[str, Any]:
    spurious_freqs: List[float] = [compute_mean_spatial_frequency(p) for p in spurious_patches]
    core_freqs: List[float] = [compute_mean_spatial_frequency(p) for p in core_patches]

    spurious_mean = float(np.mean(spurious_freqs))
    core_mean = float(np.mean(core_freqs))

    t_stat, p_value = stats.ttest_ind(spurious_freqs, core_freqs, equal_var=False)

    return {
        "spurious_mean_freq": spurious_mean,
        "core_mean_freq": core_mean,
        "spurious_freqs": spurious_freqs,
        "core_freqs": core_freqs,
        "t_stat": float(t_stat),
        "p_value": float(p_value),
        "direction_correct": spurious_mean < core_mean,
    }
