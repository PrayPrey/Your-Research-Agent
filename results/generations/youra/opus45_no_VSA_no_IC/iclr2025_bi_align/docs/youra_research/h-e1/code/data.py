"""Data loading and filtering for Chatbot Arena battles."""

import pandas as pd
from datasets import load_dataset
from config import CONFIG


def load_battles(dataset_id: str) -> pd.DataFrame:
    """Load raw Arena battles via datasets.load_dataset."""
    ds = load_dataset(dataset_id, split="train")
    return ds.to_pandas()


def filter_valid(df: pd.DataFrame) -> pd.DataFrame:
    """Keep rows where winner is valid and responses exist."""
    df = df.copy()

    if "winner" not in df.columns:
        df["winner"] = "tie"
        df.loc[df["winner_model_a"] == 1, "winner"] = "model_a"
        df.loc[df["winner_model_b"] == 1, "winner"] = "model_b"

    mask = df["prompt"].notna() & (df["prompt"].str.len() > 0)
    mask &= df["response_a"].notna() & (df["response_a"].str.len() > 0)
    mask &= df["response_b"].notna() & (df["response_b"].str.len() > 0)
    return df[mask].reset_index(drop=True)


def prepare_battles(df: pd.DataFrame) -> pd.DataFrame:
    """Rename columns to standard format."""
    df = df.copy()
    df["resp_a"] = df["response_a"]
    df["resp_b"] = df["response_b"]
    return df
