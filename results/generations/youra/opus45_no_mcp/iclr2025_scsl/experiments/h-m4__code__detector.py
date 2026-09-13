"""H-M3 Detector: Smoothing, differentiation, and peak detection"""
import numpy as np
from scipy.ndimage import uniform_filter1d
from scipy.signal import find_peaks
from typing import Optional


def smooth_curve(wga: np.ndarray, window_size: int) -> np.ndarray:
    """Apply rolling window smoothing with edge handling."""
    if len(wga) < window_size:
        return np.zeros_like(wga)
    return uniform_filter1d(wga, size=window_size, mode='nearest')


def second_derivative(smoothed: np.ndarray) -> np.ndarray:
    """Compute second derivative via double np.gradient."""
    d1 = np.gradient(smoothed)
    d2 = np.gradient(d1)
    return d2


def detect_peak(d2_wga: np.ndarray, prominence: float = 0.005) -> dict:
    """Detect crystallization peak as significant negative peak in d²WGA/dt².

    Returns: {detected, epoch, prominence, snr}
    """
    if len(d2_wga) < 5:
        return {'detected': False, 'epoch': None, 'prominence': None, 'snr': None}
    neg_d2 = -d2_wga
    peaks, props = find_peaks(neg_d2, prominence=prominence)
    if len(peaks) == 0:
        return {'detected': False, 'epoch': None, 'prominence': None, 'snr': None}
    best_idx = np.argmax(props['prominences'])
    peak_epoch = int(peaks[best_idx])
    peak_prominence = float(props['prominences'][best_idx])
    noise_std = np.std(d2_wga)
    snr = peak_prominence / noise_std if noise_std > 1e-10 else float('inf')
    return {
        'detected': True,
        'epoch': peak_epoch,
        'prominence': peak_prominence,
        'snr': float(snr)
    }


def run_sensitivity_analysis(wga: np.ndarray, windows: list = None,
                              prominence: float = 0.005) -> dict:
    """Run detection across multiple smoothing windows.

    Returns: {str(window): detect_peak_result}
    """
    if windows is None:
        windows = [3, 5, 7]
    results = {}
    for w in windows:
        smoothed = smooth_curve(wga, w)
        d2 = second_derivative(smoothed)
        peak_info = detect_peak(d2, prominence)
        results[f'w{w}'] = peak_info
    return results
