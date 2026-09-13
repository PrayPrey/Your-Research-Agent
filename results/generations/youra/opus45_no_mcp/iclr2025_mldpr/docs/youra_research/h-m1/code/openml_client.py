"""OpenML client for fetching vision dataset metadata."""
import pandas as pd
import openml
from config import CONFIG


def fetch_vision_datasets() -> pd.DataFrame:
    """Fetch image classification datasets from OpenML, filtered by vision keywords."""
    datasets = openml.datasets.list_datasets(output_format='dataframe')

    mask = datasets['name'].str.lower().str.contains(
        '|'.join(CONFIG.vision_keywords), na=False
    )
    vision_df = datasets[mask].copy()

    if 'NumberOfRuns' in vision_df.columns:
        vision_df['run_count'] = vision_df['NumberOfRuns'].fillna(0).astype(int)
    elif 'runs' in vision_df.columns:
        vision_df['run_count'] = vision_df['runs'].fillna(0).astype(int)
    else:
        vision_df['run_count'] = 0

    vision_df = vision_df.sort_values('run_count', ascending=False)
    return vision_df[['name', 'run_count', 'NumberOfInstances']].reset_index(drop=True)


def select_high_low_groups(df: pd.DataFrame) -> tuple:
    """Select top-N high-use and bottom-N low-use datasets."""
    high = df.head(CONFIG.n_high)[['name', 'run_count']].to_dict('records')
    low = df.tail(CONFIG.n_low)[['name', 'run_count']].to_dict('records')
    return high, low
