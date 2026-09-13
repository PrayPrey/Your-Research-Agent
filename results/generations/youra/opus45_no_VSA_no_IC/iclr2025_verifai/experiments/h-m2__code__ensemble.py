import pandas as pd

def normalize_minmax(series: pd.Series) -> pd.Series:
    min_val, max_val = series.min(), series.max()
    if max_val == min_val:
        return pd.Series([0.5] * len(series), index=series.index)
    return (series - min_val) / (max_val - min_val)

def compute_ensemble_score(
    df: pd.DataFrame,
    weights: dict[str, float],
    metrics: list[str] = ["pylint_score", "radon_cc"],
) -> pd.DataFrame:
    df = df.copy()
    ensemble = pd.Series([0.0] * len(df), index=df.index)
    for metric in metrics:
        norm = normalize_minmax(df[metric])
        ensemble += weights[metric] * norm
    df["ensemble"] = ensemble
    return df
