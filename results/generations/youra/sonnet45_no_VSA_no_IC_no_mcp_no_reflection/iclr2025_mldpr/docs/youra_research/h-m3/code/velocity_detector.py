"""Citation velocity detector with spike detection."""
import pandas as pd
import numpy as np
from typing import Tuple


class VelocityDetector:
    def __init__(self, velocity_window: int = 3, spike_threshold: float = 2.0):
        """Initialize velocity detector."""
        self.velocity_window = velocity_window
        self.spike_threshold = spike_threshold

    def compute_velocity(self, citation_df: pd.DataFrame) -> pd.Series:
        """
        Compute monthly citation velocity with rolling window smoothing.

        Args:
            citation_df: DataFrame[date: str, citations: int]

        Returns:
            pd.Series[date -> velocity: float]
        """
        df = citation_df.copy()
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')

        # Rolling differentiation: (citations[t] - citations[t-window]) / window
        velocity = (
            df['citations']
            .rolling(window=self.velocity_window)
            .apply(lambda x: (x.iloc[-1] - x.iloc[0]) / self.velocity_window if len(x) == self.velocity_window else np.nan)
        )

        velocity.index = df['date']
        return velocity

    def detect_spike(
        self,
        velocity_series: pd.Series,
        window_start: str,
        window_end: str
    ) -> Tuple[bool, float]:
        """
        Detect velocity spike in time window (>2σ above mean).

        Args:
            velocity_series: pd.Series[date -> velocity]
            window_start: Start date (YYYY-MM)
            window_end: End date (YYYY-MM)

        Returns:
            (spike_detected: bool, max_velocity: float)
        """
        start = pd.to_datetime(window_start)
        end = pd.to_datetime(window_end)

        window = velocity_series[(velocity_series.index >= start) & (velocity_series.index <= end)]
        window_clean = window.dropna()

        if len(window_clean) == 0:
            return False, 0.0

        mean = window_clean.mean()
        std = window_clean.std()
        max_vel = window_clean.max()

        # Spike if max > mean + threshold*std
        spike = max_vel > (mean + self.spike_threshold * std) if std > 0 else False
        return spike, max_vel
