"""Manual inspection baseline."""

from typing import Optional
import pandas as pd


def manual_inspection_baseline(df: pd.DataFrame) -> Optional[pd.Timestamp]:
    """
    Naive baseline. df: [N, 2] -> first_decay_date.
    Rule: 6mo with <1% total improvement.
    """
    window_size = 180  # days

    for i in range(len(df) - window_size):
        window = df.iloc[i : i + window_size]

        if len(window) < 10:
            continue

        total_change = window['score'].iloc[-1] - window['score'].iloc[0]
        relative_change = total_change / window['score'].iloc[0]

        if relative_change < 0.01:  # <1% improvement
            return window['date'].iloc[0]

    return None
