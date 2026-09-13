"""DNSI computation and baseline metrics."""

import numpy as np
from datetime import datetime, timedelta
from scipy.stats import entropy
from config import CONFIG


class DNSIComputer:
    """Difficulty-Normalized Saturation Index computer."""

    def __init__(self, window_months: int = 6):
        self.window_months = window_months

    def compute_dnsi(
        self,
        sota_history: list[tuple[datetime, float]],
        difficulty_proxy: int | None,
    ) -> float | None:
        """Compute DNSI from SOTA history. Returns None if uncomputable."""
        if len(sota_history) < 2:
            return None
        if difficulty_proxy is None or difficulty_proxy <= 1:
            return None

        deltas = self._compute_windowed_improvements(sota_history)
        if deltas.size == 0 or deltas.sum() == 0:
            return None

        probs = deltas / deltas.sum()
        h_observed = entropy(probs)
        h_max = np.log(difficulty_proxy)

        if h_max == 0:
            return None

        dnsi = h_observed / h_max
        return float(np.clip(dnsi, *CONFIG["dnsi_valid_range"]))

    def _compute_windowed_improvements(
        self, sota_history: list[tuple[datetime, float]]
    ) -> np.ndarray:
        """Aggregate improvements into window_months-wide buckets."""
        window_delta = timedelta(days=self.window_months * 30)
        start_date = sota_history[0][0]
        end_date = sota_history[-1][0]

        improvements = []
        current = start_date
        prev_max = sota_history[0][1]

        while current < end_date:
            window_end = current + window_delta
            window_accs = [
                acc for dt, acc in sota_history
                if current <= dt < window_end
            ]
            if window_accs:
                window_max = max(window_accs)
                if window_max > prev_max:
                    improvements.append(window_max - prev_max)
                    prev_max = window_max
            current = window_end

        return np.array(improvements) if improvements else np.array([])


def compute_raw_entropy(sota_history: list[tuple[datetime, float]]) -> float | None:
    """Compute raw Shannon entropy of accuracy deltas."""
    if len(sota_history) < 2:
        return None
    deltas = [sota_history[i][1] - sota_history[i-1][1]
              for i in range(1, len(sota_history))
              if sota_history[i][1] > sota_history[i-1][1]]
    if not deltas:
        return None
    deltas = np.array(deltas)
    probs = deltas / deltas.sum()
    return float(entropy(probs))


def compute_improvement_rate(sota_history: list[tuple[datetime, float]]) -> float | None:
    """Compute mean accuracy improvement per year."""
    if len(sota_history) < 2:
        return None
    total_improvement = sota_history[-1][1] - sota_history[0][1]
    span_years = (sota_history[-1][0] - sota_history[0][0]).days / 365
    if span_years <= 0:
        return None
    return total_improvement / span_years


def compute_time_since_last_sota(
    sota_history: list[tuple[datetime, float]],
    reference_date: datetime | None = None
) -> int | None:
    """Compute days since last SOTA improvement."""
    if not sota_history:
        return None
    if reference_date is None:
        reference_date = datetime.now()
    return (reference_date - sota_history[-1][0]).days


def validate_dnsi(dnsi_value: float | None) -> bool:
    """Check if DNSI value is valid."""
    if dnsi_value is None:
        return False
    low, high = CONFIG["dnsi_valid_range"]
    return np.isfinite(dnsi_value) and low <= dnsi_value <= high
