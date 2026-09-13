import numpy as np
from scipy.ndimage import uniform_filter1d
from scipy.stats import pearsonr

def compute_inflection_epoch(gradient_ratio_history: list, smoothing_window: int = 5) -> tuple:
    ratio = np.array(gradient_ratio_history)
    if len(ratio) < smoothing_window:
        return 0, np.zeros_like(ratio)
    smoothed = uniform_filter1d(ratio, size=smoothing_window)
    d1 = np.gradient(smoothed)
    d2 = np.gradient(d1)
    midpoint = max(1, len(d2) // 2)
    inflection_epoch = int(np.argmin(d2[:midpoint]))
    return inflection_epoch, d1

def correlate_with_wga(
    inflection_epoch: int,
    wga_peak_epoch: int,
    gradient_ratio_history: list,
    wga_history: list,
    n_epochs: int
) -> dict:
    gradient_arr = np.array(gradient_ratio_history)
    wga_arr = np.array(wga_history)
    min_len = min(len(gradient_arr), len(wga_arr))
    if min_len < 2:
        return {
            'r': 0.0,
            'p_value': 1.0,
            'inflection_epoch': inflection_epoch,
            'wga_peak_epoch': wga_peak_epoch,
            'temporal_precedence': inflection_epoch <= wga_peak_epoch,
            'gate_pass': False
        }
    r, p_value = pearsonr(gradient_arr[:min_len], wga_arr[:min_len])
    temporal_precedence = inflection_epoch <= wga_peak_epoch
    gate_pass = (abs(r) > 0.7) and (inflection_epoch < n_epochs // 2)
    return {
        'r': float(r),
        'p_value': float(p_value),
        'inflection_epoch': inflection_epoch,
        'wga_peak_epoch': wga_peak_epoch,
        'temporal_precedence': temporal_precedence,
        'gate_pass': gate_pass
    }
