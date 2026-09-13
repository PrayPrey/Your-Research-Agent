import pandas as pd
from sklearn.preprocessing import StandardScaler


def load_and_validate(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path, index_col=0)
    df = df.dropna(subset=['win_rate', 'length_controlled_winrate', 'avg_length'])
    assert len(df) >= 200, f"Expected >=200 models, got {len(df)}"
    return df


def standardize(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    scaler_win = StandardScaler()
    scaler_len = StandardScaler()
    df['win_rate_std'] = scaler_win.fit_transform(df[['win_rate']])
    df['avg_length_std'] = scaler_len.fit_transform(df[['avg_length']])
    assert abs(df['win_rate_std'].mean()) < 1e-10, "win_rate_std mean not ~0"
    assert abs(df['win_rate_std'].std(ddof=0) - 1.0) < 1e-6, "win_rate_std std not ~1"
    assert abs(df['avg_length_std'].mean()) < 1e-10, "avg_length_std mean not ~0"
    assert abs(df['avg_length_std'].std(ddof=0) - 1.0) < 1e-6, "avg_length_std std not ~1"
    return df
