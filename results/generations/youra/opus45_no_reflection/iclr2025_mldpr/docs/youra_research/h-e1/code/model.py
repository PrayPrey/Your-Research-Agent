"""H-E1 Models: Baseline (Monotonic) and Proposed (PELT Change-Point)"""
import numpy as np
from scipy import stats
import ruptures as rpt
from config import PELT, EVAL


class MonotonicTrendModel:
    """H0: single linear trend over full series."""

    def __init__(self):
        self.slope = None
        self.intercept = None
        self.r_value = None
        self._residuals = None
        self._predictions = None

    def fit(self, t: np.ndarray, y: np.ndarray) -> "MonotonicTrendModel":
        """Fit linear regression: y = slope * t + intercept."""
        t = np.asarray(t)
        y = np.asarray(y)

        result = stats.linregress(t, y)
        self.slope = result.slope
        self.intercept = result.intercept
        self.r_value = result.rvalue

        self._predictions = self.slope * t + self.intercept
        self._residuals = y - self._predictions

        return self

    def predict(self, t: np.ndarray) -> np.ndarray:
        """Predict y values for given t."""
        return self.slope * np.asarray(t) + self.intercept

    def residuals(self) -> np.ndarray:
        return self._residuals

    def predictions(self) -> np.ndarray:
        return self._predictions

    def r_squared(self) -> float:
        return self.r_value ** 2


class GiniChangePointDetector:
    """H1: PELT segmented trend."""

    def __init__(
        self,
        model: str = None,
        min_size: int = None,
        target_window: tuple = None,
    ):
        self.model = model or PELT.model
        self.min_size = min_size or PELT.min_size
        self.target_window = target_window or EVAL.target_window

        self.change_points = None
        self.target_hit = False
        self._segment_models = []
        self._segment_residuals = []
        self._segment_predictions = None

    def detect(
        self,
        gini_series: np.ndarray,
        dates=None,
        penalty: float = None
    ) -> tuple:
        """PELT change-point detection.

        Args:
            gini_series: 1D array of Gini values
            dates: Optional DatetimeIndex for target window check
            penalty: If None, uses BIC-based penalty: log(n) * var(signal)

        Returns:
            (change_points: list[int], target_hit: bool)
        """
        gini_series = np.asarray(gini_series).reshape(-1, 1)
        n = len(gini_series)

        if penalty is None:
            # Use much higher penalty multiplier to get sparse meaningful CPs
            # Standard BIC: log(n) * var, but with low variance we need ~100x
            # Calibrated to detect 1-3 structural breaks rather than noise
            penalty = 100 * np.log(n) * np.var(gini_series)

        algo = rpt.Pelt(model=self.model, min_size=self.min_size, jump=1)
        algo.fit(gini_series)

        # predict returns change points INCLUDING the final index n
        raw_cps = algo.predict(pen=penalty)
        # actual breakpoints are all except the last (which is always n)
        self.change_points = [cp for cp in raw_cps if cp < n]

        # Check if any change point falls in target window
        self.target_hit = False
        if dates is not None and len(self.change_points) > 0:
            for cp in self.change_points:
                if cp < len(dates):
                    year = dates[cp].year
                    if self.target_window[0] <= year <= self.target_window[1]:
                        self.target_hit = True
                        break
        elif len(self.change_points) > 0:
            # If no dates provided, assume 2018 start (index 0 = Jan 2018)
            # Target window 2019-2022 = indices 12-59 (months 13-60)
            for cp in self.change_points:
                year = 2018 + cp // 12
                if self.target_window[0] <= year <= self.target_window[1]:
                    self.target_hit = True
                    break

        return self.change_points, self.target_hit

    def fit_segmented_trends(
        self, t: np.ndarray, y: np.ndarray, change_points: list = None
    ) -> list:
        """Fit linear trend per segment defined by change_points.

        Returns:
            list of per-segment residual arrays
        """
        if change_points is None:
            change_points = self.change_points or []

        t = np.asarray(t)
        y = np.asarray(y)
        n = len(t)

        # Create segment boundaries: [0, cp1, cp2, ..., n]
        boundaries = [0] + list(change_points) + [n]
        # Remove duplicates and sort
        boundaries = sorted(set(boundaries))

        self._segment_models = []
        self._segment_residuals = []
        self._segment_predictions = np.zeros_like(y)

        for i in range(len(boundaries) - 1):
            start = boundaries[i]
            end = boundaries[i + 1]

            if end - start < 2:
                # Too short for regression, use mean
                seg_pred = np.full(end - start, np.mean(y[start:end]))
                seg_resid = y[start:end] - seg_pred
                self._segment_models.append(None)
            else:
                seg_t = t[start:end]
                seg_y = y[start:end]
                result = stats.linregress(seg_t, seg_y)
                seg_pred = result.slope * seg_t + result.intercept
                seg_resid = seg_y - seg_pred
                self._segment_models.append(result)

            self._segment_predictions[start:end] = seg_pred
            self._segment_residuals.append(seg_resid)

        return self._segment_residuals

    def segment_predictions(self) -> np.ndarray:
        return self._segment_predictions

    def all_residuals(self) -> np.ndarray:
        """Concatenate all segment residuals."""
        if not self._segment_residuals:
            return np.array([])
        return np.concatenate(self._segment_residuals)


if __name__ == "__main__":
    # Test with synthetic data
    np.random.seed(42)
    t = np.arange(72)
    # Simulate change point at t=36 (month 37, ~2021)
    y = np.where(t < 36, 0.6 + 0.002 * t, 0.7 - 0.003 * (t - 36)) + np.random.normal(0, 0.02, 72)

    print("Testing MonotonicTrendModel...")
    mono = MonotonicTrendModel().fit(t, y)
    print(f"  R²: {mono.r_squared():.4f}")

    print("\nTesting GiniChangePointDetector...")
    det = GiniChangePointDetector()
    cps, hit = det.detect(y)
    print(f"  Change points: {cps}")
    print(f"  Target hit: {hit}")

    det.fit_segmented_trends(t, y, cps)
    print(f"  Num segments: {len(det._segment_residuals)}")
