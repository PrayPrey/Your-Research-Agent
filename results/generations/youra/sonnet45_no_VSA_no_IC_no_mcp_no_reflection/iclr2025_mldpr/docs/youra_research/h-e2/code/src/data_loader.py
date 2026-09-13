"""Data loading for PWC benchmark leaderboards."""

from pathlib import Path
from typing import Optional
import pandas as pd


def load_pwc_benchmark(benchmark_id: str, cache_dir: Optional[Path] = None) -> pd.DataFrame:
    """
    Fetch PWC benchmark data.
    Returns: DataFrame with columns ['date', 'score', 'model', 'paper']
    """
    if cache_dir is None:
        cache_dir = Path(__file__).parent.parent / 'data'

    data_file = cache_dir / f'{benchmark_id}_leaderboard.csv'

    if not data_file.exists():
        raise FileNotFoundError(f"Dataset not found: {data_file}")

    df = pd.read_csv(data_file)
    df['date'] = pd.to_datetime(df['date'])

    return df


def preprocess_leaderboard(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean data. df: [N rows x 4 cols] -> [M rows x 2 cols where M<=N].
    Keeps date, score only.
    """
    # Filter missing values
    df = df.dropna(subset=['date', 'score'])

    # Remove duplicates (keep highest score per date)
    df = df.sort_values(['date', 'score'], ascending=[True, False])
    df = df.drop_duplicates(subset=['date'], keep='first')

    # Keep only date and score columns
    df = df[['date', 'score']].copy()

    # Sort chronologically
    df = df.sort_values('date').reset_index(drop=True)

    return df
