from typing import Iterable
import pandas as pd
from datasets import load_dataset


def load_wildchat(split: str = "train") -> Iterable[dict]:
    ds = load_dataset("allenai/WildChat-1M", split=split, streaming=True)
    return ds


def load_lmsys() -> pd.DataFrame:
    # Primary: gated, requires HF access
    try:
        ds = load_dataset("lmsys/chatbot_arena_conversations", split="train")
        df = ds.to_pandas()
        df["month"] = pd.to_datetime(df["tstamp"], unit="s").dt.to_period("M").astype(str)
        df["winner"] = df["winner"].replace("tie (bothbad)", "tie")
        return df[["model_a", "model_b", "winner", "month"]]
    except Exception as e:
        print(f"[DataLoader] Primary LMSYS failed ({type(e).__name__}: {e}), using fallback")

    # Fallback: lmsys-arena-human-preference-55k (no timestamps)
    # Reconstruct winner column from binary flags; no temporal data -> return empty
    try:
        ds = load_dataset("lmsys/lmsys-arena-human-preference-55k", split="train")
        df = ds.to_pandas()
        # Reconstruct winner
        def get_winner(row):
            if row.get("winner_model_a", 0) == 1:
                return "model_a"
            elif row.get("winner_model_b", 0) == 1:
                return "model_b"
            else:
                return "tie"
        df["winner"] = df.apply(get_winner, axis=1)
        # No timestamps available — assign NaT month so downstream filters drop all rows
        df["month"] = pd.NaT
        df["month"] = df["month"].astype(str)  # "NaT" -> will be filtered by date range
        print("[DataLoader] Fallback LMSYS loaded but has no timestamps; Proxy 2 will be empty")
        return df[["model_a", "model_b", "winner", "month"]]
    except Exception as e2:
        print(f"[DataLoader] Fallback LMSYS also failed ({e2}); returning empty DataFrame")
        return pd.DataFrame(columns=["model_a", "model_b", "winner", "month"])
