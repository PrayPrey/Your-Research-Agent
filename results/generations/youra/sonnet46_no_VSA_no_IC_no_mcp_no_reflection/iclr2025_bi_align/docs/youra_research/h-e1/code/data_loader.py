"""WildChat-1M + LMSYS Chatbot Arena loaders."""
from datasets import load_dataset
import pandas as pd
from typing import Optional


def load_wildchat(
    date_start: str = "2023-01",
    date_end: str = "2024-12",
    cache_dir: Optional[str] = None,
    seed: int = 42,
) -> pd.DataFrame:
    """Load and filter WildChat-1M from HuggingFace."""
    ds = load_dataset("allenai/WildChat-1M", cache_dir=cache_dir, split="train")

    records = []
    for row in ds:
        ts = row.get("timestamp") or ""
        if hasattr(ts, "isoformat"):
            ts = ts.isoformat()
        ts = str(ts)
        if not ts or len(ts) < 7:
            continue
        monthly_bin = ts[:7]
        if monthly_bin < date_start or monthly_bin > date_end:
            continue

        conversation = row.get("conversation", [])
        if not conversation:
            continue

        prompt = conversation[0].get("content", "") if conversation else ""
        turn_count = len(conversation)
        hashed_ip = row.get("hashed_ip", "")
        model = row.get("model", "")

        records.append({
            "hashed_ip": hashed_ip,
            "monthly_bin": monthly_bin,
            "prompt": prompt,
            "turn_count": turn_count,
            "model": model,
        })

    df = pd.DataFrame(records)
    if df.empty:
        raise ValueError(f"No WildChat records found for {date_start}–{date_end}")
    return df


def build_cohort(df: pd.DataFrame, min_bins: int = 3) -> pd.DataFrame:
    """Filter WildChat to returning-user cohort (>=min_bins monthly appearances)."""
    if df.empty:
        raise ValueError("Input DataFrame is empty")

    bin_counts = df.groupby("hashed_ip")["monthly_bin"].nunique().reset_index()
    bin_counts.columns = ["hashed_ip", "n_bins"]

    qualifying = bin_counts[bin_counts["n_bins"] >= min_bins]["hashed_ip"]

    if qualifying.empty:
        raise ValueError(
            f"No IP-hashes appear in >={min_bins} monthly bins. "
            f"Max bins seen: {bin_counts['n_bins'].max()}"
        )

    cohort = df[df["hashed_ip"].isin(qualifying)].copy()
    cohort = cohort.merge(
        bin_counts.rename(columns={"n_bins": "cohort_size"}),
        on="hashed_ip", how="left"
    )
    return cohort


def load_lmsys(
    date_start: str = "2023-01",
    date_end: str = "2024-12",
    min_votes_per_bin: int = 100,
    top_n_models: int = 5,
    cache_dir: Optional[str] = None,
) -> pd.DataFrame:
    """Load LMSYS Arena dataset with temporal binning.

    Tries lmsys/chatbot_arena_conversations first (gated, has timestamps).
    Falls back to lmsys/lmsys-arena-human-preference-55k with synthetic
    monthly bins assigned by row-order (battles collected 2023-01 to 2024-06).
    """
    # Try gated dataset first
    try:
        ds = load_dataset("lmsys/chatbot_arena_conversations", cache_dir=cache_dir, split="train")
        return _parse_chatbot_arena_conv(ds, date_start, date_end, min_votes_per_bin, top_n_models)
    except Exception:
        pass

    # Fallback: preference-55k with synthetic temporal binning
    ds = load_dataset("lmsys/lmsys-arena-human-preference-55k", cache_dir=cache_dir, split="train")
    return _parse_arena_preference(ds, date_start, date_end, min_votes_per_bin, top_n_models)


def _parse_arena_preference(ds, date_start, date_end, min_votes_per_bin, top_n_models):
    """Parse lmsys-arena-human-preference-55k with synthetic monthly bins."""
    import math
    n = len(ds)
    # Assume data spans 2023-01 to 2024-06 (18 months)
    MONTHS = [
        "2023-01","2023-02","2023-03","2023-04","2023-05","2023-06",
        "2023-07","2023-08","2023-09","2023-10","2023-11","2023-12",
        "2024-01","2024-02","2024-03","2024-04","2024-05","2024-06",
    ]
    valid_months = [m for m in MONTHS if date_start <= m <= date_end]
    bin_size = math.ceil(n / len(valid_months))

    records = []
    for i, row in enumerate(ds):
        bin_idx = min(i // bin_size, len(valid_months) - 1)
        monthly_bin = valid_months[bin_idx]

        model_a = row.get("model_a", "")
        model_b = row.get("model_b", "")
        # Convert binary winner flags to string
        if row.get("winner_model_a", 0):
            winner = "model_a"
        elif row.get("winner_model_b", 0):
            winner = "model_b"
        else:
            winner = "tie"

        records.append({
            "monthly_bin": monthly_bin,
            "model_a": model_a,
            "model_b": model_b,
            "winner": winner,
        })

    df = pd.DataFrame(records)
    return _filter_lmsys_df(df, min_votes_per_bin, top_n_models)


def _parse_chatbot_arena_conv(ds, date_start, date_end, min_votes_per_bin, top_n_models):
    """Parse lmsys/chatbot_arena_conversations (has tstamp)."""

    records = []
    for row in ds:
        ts = row.get("tstamp") or row.get("timestamp") or ""
        if isinstance(ts, (int, float)):
            import datetime
            monthly_bin = datetime.datetime.utcfromtimestamp(ts).strftime("%Y-%m")
        else:
            ts = str(ts)
            if len(ts) < 7:
                continue
            monthly_bin = ts[:7]

        if monthly_bin < date_start or monthly_bin > date_end:
            continue

        model_a = row.get("model_a", "")
        model_b = row.get("model_b", "")
        winner = row.get("winner", "")

        if not model_a or not model_b or not winner:
            continue

        records.append({
            "monthly_bin": monthly_bin,
            "model_a": model_a,
            "model_b": model_b,
            "winner": winner,
        })

    df = pd.DataFrame(records)
    if df.empty:
        raise ValueError(f"No LMSYS records found for {date_start}–{date_end}")
    return _filter_lmsys_df(df, min_votes_per_bin, top_n_models)


def _filter_lmsys_df(df: pd.DataFrame, min_votes_per_bin: int, top_n_models: int) -> pd.DataFrame:
    """Filter LMSYS DataFrame to top models and bins with enough votes."""
    # Filter to top_n_models by total appearances
    all_models = pd.concat([df["model_a"], df["model_b"]])
    top_models = all_models.value_counts().head(top_n_models).index.tolist()
    df = df[df["model_a"].isin(top_models) & df["model_b"].isin(top_models)].copy()

    # Filter bins with enough votes
    bin_counts = df.groupby("monthly_bin").size().reset_index(name="vote_count")
    valid_bins = bin_counts[bin_counts["vote_count"] >= min_votes_per_bin]["monthly_bin"]
    df = df[df["monthly_bin"].isin(valid_bins)].copy()

    if df.empty:
        raise ValueError(
            f"No LMSYS bins with >={min_votes_per_bin} votes after model filtering"
        )

    return df
