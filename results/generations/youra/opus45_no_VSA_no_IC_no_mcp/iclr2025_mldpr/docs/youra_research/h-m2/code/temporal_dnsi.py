"""Temporal DNSI computation with cutoff date filtering."""

from datetime import datetime
from m2_config import CUTOFF_DATE, MIN_PRE_CUTOFF_ENTRIES, MIN_HISTORY_YEARS_PRE_CUTOFF


class TemporalDNSIComputer:
    """Wrapper around h-e1 DNSIComputer with temporal cutoff filtering."""

    def __init__(self, dnsi_computer, cutoff_date: str = CUTOFF_DATE):
        self.cutoff = datetime.fromisoformat(cutoff_date)
        self._dnsi = dnsi_computer

    def compute_dnsi_pre_cutoff(
        self,
        sota_history: list[tuple[datetime, float]],
        difficulty_proxy: int | None,
    ) -> float | None:
        """Filter history < cutoff, enforce min entries/years, delegate to h-e1."""
        pre = [(dt, acc) for dt, acc in sota_history if dt < self.cutoff]
        pre = sorted(pre, key=lambda t: t[0])

        if len(pre) < MIN_PRE_CUTOFF_ENTRIES:
            return None

        if len(pre) < 2:
            return None

        span_years = (pre[-1][0] - pre[0][0]).days / 365
        if span_years < MIN_HISTORY_YEARS_PRE_CUTOFF:
            return None

        return self._dnsi.compute_dnsi(pre, difficulty_proxy)
