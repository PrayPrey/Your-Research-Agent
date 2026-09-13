import pandas as pd


def load_and_validate(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path, index_col=0)
    df = df.dropna(subset=['win_rate', 'length_controlled_winrate', 'avg_length'])
    assert len(df) >= 200, f"Expected >=200 models, got {len(df)}"
    return df
