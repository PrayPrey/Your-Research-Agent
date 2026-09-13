"""
Adoption date detector for h-m2 temporal lead time validation.
Rolling average threshold detection algorithm.
"""
import pandas as pd
import numpy as np
from typing import Optional
from config import ADOPTION_THRESHOLD, ADOPTION_WINDOW


class AdoptionDetector:
    """Detect paradigm shift adoption dates via citation threshold."""

    def __init__(self, threshold: int = ADOPTION_THRESHOLD, window: int = ADOPTION_WINDOW):
        """
        Initialize adoption detector.

        Args:
            threshold: Citations/month threshold
            window: Sustained months required
        """
        self.threshold = threshold
        self.window = window

    def detect_adoption_date(self, citation_timeseries: pd.DataFrame) -> Optional[str]:
        """
        Find first month where citations >= threshold for window months.

        Args:
            citation_timeseries: DataFrame with columns [date: str, citations: int]

        Returns:
            Adoption date (YYYY-MM) or None if no sustained surge found
        """
        if len(citation_timeseries) < self.window:
            return None

        # Smooth citation time series
        smoothed = self.smooth_citations(citation_timeseries)

        # Find first sustained window above threshold
        streak_start = None
        for i, (date, cit) in enumerate(zip(citation_timeseries['date'], smoothed)):
            is_above = cit >= self.threshold

            if is_above and streak_start is None:
                streak_start = i
            elif not is_above:
                streak_start = None

            # Check if sustained window reached
            if streak_start is not None and (i - streak_start + 1) >= self.window:
                adoption_date = citation_timeseries.iloc[streak_start]['date']
                print(f"Adoption detected at {adoption_date} (smoothed: {smoothed[streak_start]:.1f} cit/mo)")
                return adoption_date

        return None

    def smooth_citations(self, df: pd.DataFrame) -> pd.Series:
        """
        Apply 3-month rolling average to citation time series.

        Args:
            df: DataFrame with citations column

        Returns:
            Series with smoothed citation counts
        """
        return df['citations'].rolling(window=3, min_periods=1).mean()


if __name__ == "__main__":
    # Test adoption detector
    from citation_fetcher import CitationFetcher
    import json

    detector = AdoptionDetector()
    fetcher = CitationFetcher()

    papers = ['gpt3', 'vit', 'llama']
    adoption_dates = {}

    for paper_id in papers:
        # Load cached citation data
        cache_file = fetcher.cache_dir / f"{paper_id}.json"
        if cache_file.exists():
            with open(cache_file) as f:
                data = json.load(f)
            df = pd.DataFrame(data)

            adoption_date = detector.detect_adoption_date(df)
            adoption_dates[paper_id] = adoption_date
            print(f"{paper_id}: {adoption_date}")
        else:
            print(f"No citation data for {paper_id}")

    # Save adoption dates
    from pathlib import Path
    output_file = Path(__file__).parent.parent / "data" / "shift_adoption_dates.json"
    with open(output_file, 'w') as f:
        json.dump(adoption_dates, f, indent=2)
    print(f"\nSaved adoption dates to {output_file}")
