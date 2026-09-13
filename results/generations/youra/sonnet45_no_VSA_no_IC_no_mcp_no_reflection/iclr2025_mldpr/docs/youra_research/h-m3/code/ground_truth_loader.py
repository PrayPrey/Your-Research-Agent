"""Ground truth loader for paradigm shift labels."""
import json
from pathlib import Path
from typing import Dict
import pandas as pd


class GroundTruthLoader:
    def load_paradigm_shifts(self, path: Path) -> Dict[str, str]:
        """Load paradigm shift dates from JSON."""
        with open(path) as f:
            return json.load(f)

    def create_labels(
        self,
        saturation_dates: Dict[str, str],
        shift_dates: Dict[str, str],
        threshold_months: int = 6
    ) -> Dict[str, int]:
        """
        Create binary labels (shift within threshold of saturation).

        Returns:
            Dict[benchmark -> label {0, 1}]
        """
        labels = {}
        for benchmark in saturation_dates.keys():
            if benchmark not in shift_dates:
                labels[benchmark] = 0
                continue

            sat_date = pd.to_datetime(saturation_dates[benchmark])
            shift_date = pd.to_datetime(shift_dates[benchmark])

            # Label = 1 if shift occurs within threshold_months AFTER saturation
            months_diff = (shift_date.year - sat_date.year) * 12 + (shift_date.month - sat_date.month)
            labels[benchmark] = 1 if 0 <= months_diff <= threshold_months else 0

        return labels
