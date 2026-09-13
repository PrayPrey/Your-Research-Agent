"""Correlation detector combining saturation + citation velocity."""
import pandas as pd
from typing import Dict, List
from dateutil.relativedelta import relativedelta
from velocity_detector import VelocityDetector


class CorrelationDetector:
    def __init__(
        self,
        saturation_dates: Dict[str, str],
        velocity_detector: VelocityDetector,
        search_window_pre: int = 3,
        search_window_post: int = 6
    ):
        """
        Initialize correlation detector.

        Args:
            saturation_dates: Dict[benchmark -> saturation_date (YYYY-MM)]
            velocity_detector: VelocityDetector instance
            search_window_pre: Months before saturation to search
            search_window_post: Months after saturation to search
        """
        self.saturation_dates = saturation_dates
        self.velocity_detector = velocity_detector
        self.search_window_pre = search_window_pre
        self.search_window_post = search_window_post

    def detect_shift(
        self, benchmark: str, citation_df: pd.DataFrame
    ) -> int:
        """
        Predict paradigm shift using saturation + velocity correlation.

        Args:
            benchmark: Benchmark name
            citation_df: DataFrame[date: str, citations: int]

        Returns:
            1 if shift predicted (saturation AND velocity spike), 0 otherwise
        """
        # Check saturation
        if benchmark not in self.saturation_dates:
            return 0

        saturation_date = pd.to_datetime(self.saturation_dates[benchmark])

        # Compute velocity
        velocity_series = self.velocity_detector.compute_velocity(citation_df)

        # Define search window
        window_start = saturation_date - relativedelta(months=self.search_window_pre)
        window_end = saturation_date + relativedelta(months=self.search_window_post)

        # Detect spike
        has_spike, _ = self.velocity_detector.detect_spike(
            velocity_series,
            window_start.strftime("%Y-%m"),
            window_end.strftime("%Y-%m")
        )

        return 1 if has_spike else 0

    def detect_all(
        self, benchmarks: List[str], citation_data: Dict[str, pd.DataFrame]
    ) -> Dict[str, int]:
        """
        Run detection on multiple benchmarks.

        Args:
            benchmarks: List of benchmark names
            citation_data: Dict[benchmark -> citation_df]

        Returns:
            Dict[benchmark -> prediction {0, 1}]
        """
        predictions = {}
        for benchmark in benchmarks:
            if benchmark in citation_data:
                predictions[benchmark] = self.detect_shift(benchmark, citation_data[benchmark])
            else:
                predictions[benchmark] = 0
        return predictions
