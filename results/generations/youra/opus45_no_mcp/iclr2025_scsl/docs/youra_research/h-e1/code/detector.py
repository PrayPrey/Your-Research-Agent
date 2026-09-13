import numpy as np
from scipy.ndimage import uniform_filter1d

class CrystallizationDetector:
    def __init__(self, smoothing_window: int = 5):
        self.smoothing_window = smoothing_window
        self.wga_history = []

    def log_epoch(self, wga: float) -> None:
        self.wga_history.append(wga)

    def compute_second_derivative(self) -> np.ndarray:
        wga = np.array(self.wga_history)
        if len(wga) < self.smoothing_window:
            return np.zeros_like(wga)
        smoothed = uniform_filter1d(wga, size=self.smoothing_window)
        d1 = np.gradient(smoothed)
        d2 = np.gradient(d1)
        return d2

    def detect_crystallization_peak(self, threshold: float = -0.01) -> tuple:
        d2 = self.compute_second_derivative()
        if len(d2) == 0:
            return 0, 0.0, False
        midpoint = max(1, len(d2) // 2)
        d2_early = d2[:midpoint]
        peak_idx = int(np.argmin(d2_early))
        peak_value = float(d2_early[peak_idx])
        is_significant = peak_value < threshold
        return peak_idx, peak_value, is_significant
