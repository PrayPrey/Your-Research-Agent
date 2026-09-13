"""Velocity decay detector using linear regression."""

from typing import Tuple, List, Optional
import pandas as pd
import numpy as np
from scipy.stats import linregress


class VelocityDecayDetector:
    """Detect improvement velocity decay in benchmark leaderboards."""

    def __init__(self, window_days: int = 180, threshold: float = 0.1):
        """
        Initialize detector.
        window_days: rolling window size, threshold: velocity limit (improvement/month)
        """
        self.window_days = window_days
        self.threshold = threshold

    def detect(
        self, df: pd.DataFrame
    ) -> Tuple[Optional[pd.Timestamp], List[Tuple[pd.Timestamp, float, float]]]:
        """
        Detect decay. df: [N, 2] -> (first_decay_date, velocities).
        velocities: [(date, velocity, p_value)]
        """
        velocities = []

        for i in range(len(df)):
            window_end = df.loc[i, 'date']
            window_start = window_end - pd.Timedelta(days=self.window_days)

            # Extract rolling window
            mask = (df['date'] >= window_start) & (df['date'] <= window_end)
            window = df[mask]

            if len(window) < 10:  # Need ≥10 points for regression
                continue

            velocity, p_value = self._compute_velocity(window)
            velocities.append((window_end, velocity, p_value))

            # Check detection condition
            if velocity < self.threshold and p_value < 0.05:
                return window_end, velocities

        return None, velocities

    def _compute_velocity(self, window: pd.DataFrame) -> Tuple[float, float]:
        """
        Compute slope. window: [K, 2] -> (monthly_velocity, p_value). K >= 10.
        """
        # Convert dates to numeric (days since first)
        x = (window['date'] - window['date'].min()).dt.days.values
        y = window['score'].values

        # Fit linear regression
        slope, intercept, r, p_value, std_err = linregress(x, y)

        # Convert daily to monthly
        monthly_velocity = slope * 30

        return monthly_velocity, p_value
