import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score
from typing import List, Tuple, Dict


class AgreementCalculator:
    """Calculate inter-rater agreement metrics."""

    def calculate_kappa(self, labels1: List[str], labels2: List[str]) -> float:
        """Cohen's kappa for categorical features."""
        return cohen_kappa_score(labels1, labels2)

    def calculate_icc(self, ratings: np.ndarray) -> float:
        """ICC for continuous features."""
        n, k = ratings.shape
        mean_ratings = np.mean(ratings, axis=1)
        ss_between = k * np.sum((mean_ratings - np.mean(ratings)) ** 2)
        ss_within = np.sum((ratings - mean_ratings[:, None]) ** 2)
        ms_between = ss_between / (n - 1)
        ms_within = ss_within / (n * (k - 1))
        icc = (ms_between - ms_within) / (ms_between + (k - 1) * ms_within)
        return icc

    def compute_confidence_interval(self, kappa: float, n: int) -> Tuple[float, float]:
        """95% CI via bootstrap approximation."""
        # Simplified approximation (no actual bootstrap for mock data)
        std_err = np.sqrt((1 - kappa ** 2) / n)
        margin = 1.96 * std_err
        return (max(kappa - margin, -1.0), min(kappa + margin, 1.0))

    def analyze_disagreements(
        self, labels1: List[str], labels2: List[str], benchmark_ids: List[str]
    ) -> pd.DataFrame:
        """Identify disagreement patterns."""
        disagreements = [
            {"benchmark_id": bid, "annotator1": l1, "annotator2": l2}
            for bid, l1, l2 in zip(benchmark_ids, labels1, labels2)
            if l1 != l2
        ]
        return pd.DataFrame(disagreements)
