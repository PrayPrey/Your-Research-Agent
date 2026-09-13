import pandas as pd
from typing import Tuple, Optional

class ConvergenceDetector:
    def __init__(self, window_months: int = 6, threshold: float = 0.005, top_k: int = 5):
        self.window_months = window_months
        self.threshold = threshold
        self.top_k = top_k

    def compute_rolling_std(self, df: pd.DataFrame, benchmark: str) -> pd.Series:
        benchmark_df = df[df['benchmark'] == benchmark].copy()
        benchmark_df = benchmark_df.sort_values('month')

        monthly_top_k = []
        for month in benchmark_df['month'].unique():
            month_data = benchmark_df[benchmark_df['month'] == month]
            top_scores = month_data.nlargest(self.top_k, 'score')['score']
            monthly_top_k.append({'month': month, 'std': top_scores.std()})

        monthly_std_df = pd.DataFrame(monthly_top_k).set_index('month')
        rolling_std = monthly_std_df['std'].rolling(window=self.window_months, min_periods=3).mean()
        return rolling_std

    def detect_first_convergence(self, rolling_std: pd.Series) -> Tuple[Optional[str], Optional[float]]:
        mask = rolling_std < self.threshold
        if not mask.any():
            return None, None
        first_idx = rolling_std[mask].index[0]
        return str(first_idx), rolling_std[first_idx]
