"""H-M5 Data Loader: Panel data loading and lag construction."""
import pandas as pd
from pathlib import Path

E1_DATA_PATH = Path(__file__).parent.parent.parent / "h-e1" / "code" / "results" / "hhi_metrics.csv"


def load_panel_data(path: str = None) -> pd.DataFrame:
    """Load H-E1 CSV, set MultiIndex (venue, year), sort index."""
    path = path or E1_DATA_PATH
    df = pd.read_csv(path)
    df = df.rename(columns={"n_papers": "paper_count"})
    df = df.set_index(["venue", "year"]).sort_index()
    return df[["hhi", "entropy", "paper_count"]]


def add_lags(df: pd.DataFrame, lag: int = 1) -> pd.DataFrame:
    """Groupby venue, shift hhi/entropy by lag. Add delta cols."""
    df = df.copy()
    df[f"hhi_lag{lag}"] = df.groupby(level="venue")["hhi"].shift(lag)
    df[f"entropy_lag{lag}"] = df.groupby(level="venue")["entropy"].shift(lag)
    df["delta_hhi"] = df.groupby(level="venue")["hhi"].diff()
    df["delta_entropy"] = df.groupby(level="venue")["entropy"].diff()
    return df


def prepare_analysis_df(df: pd.DataFrame, lag: int = 1) -> pd.DataFrame:
    """Add lags then dropna -> clean panel for PanelOLS."""
    return add_lags(df, lag).dropna()
