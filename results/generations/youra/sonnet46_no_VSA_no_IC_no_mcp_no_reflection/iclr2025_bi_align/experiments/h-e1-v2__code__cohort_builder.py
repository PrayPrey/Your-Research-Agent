"""Cohort construction for h-e1-v2 — vectorized Arrow-based implementation."""
from collections import defaultdict
from typing import Iterable
import glob
import re as _re
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import tiktoken

from proxy_computer import correction_freq, CORRECTION_REGEX

_ARROW_DIR = "/root/.cache/huggingface/datasets/allenai___wild_chat-1_m/default/0.0.0/7d6490e462285cf85d91eabea0f9a954fbddcd1f/"
_USER_ARROW_DIR = "/home/PrayPrey/.cache/huggingface/datasets/allenai___wild_chat-1_m/default/0.0.0/7d6490e462285cf85d91eabea0f9a954fbddcd1f/"

_PATTERN = _re.compile(CORRECTION_REGEX, _re.IGNORECASE)


def _load_wildchat_df() -> pd.DataFrame:
    """Load WildChat from cached Arrow files directly using datasets library."""
    from datasets import load_dataset
    print("[CohortBuilder] Loading WildChat from local cache (non-streaming)...")
    ds = load_dataset("allenai/WildChat-1M", split="train")
    print(f"[CohortBuilder] Loaded {len(ds)} records")
    # Convert to pandas, keeping only needed columns
    df = ds.select_columns(["hashed_ip", "timestamp", "conversation", "toxic"]).to_pandas()
    return df


def _correction_freq_vectorized(conversations: list) -> list:
    """Vectorized correction freq computation."""
    freqs = []
    for conv in conversations:
        if conv is None or len(conv) == 0:
            freqs.append(0.0)
            continue
        matches = sum(1 for turn in conv if _PATTERN.search((turn.get("content") or "") if isinstance(turn, dict) else ""))
        freqs.append(matches / len(conv))
    return freqs


def _first_user_content(conversations: list) -> list:
    result = []
    for conv in conversations:
        text = ""
        if conv is not None and len(conv) > 0:
            for turn in conv:
                if isinstance(turn, dict) and turn.get("role") == "user":
                    text = turn.get("content", "") or ""
                    break
        result.append(text)
    return result


def build_wildchat_monthly(
    stream,  # ignored — we load directly from cache
    date_start: str = "2023-01",
    date_end: str = "2024-12",
    min_bins: int = 3,
    min_cohort_size: int = 50,
    n_workers: int = 4,
) -> tuple:
    enc = tiktoken.get_encoding("cl100k_base")

    df = _load_wildchat_df()

    # Filter toxic
    df = df[~df["toxic"].fillna(False)]

    # Parse month (timestamp is datetime.datetime in pandas)
    df["month"] = pd.to_datetime(df["timestamp"], utc=True).dt.to_period("M").astype(str)
    df = df[(df["month"] >= date_start) & (df["month"] <= date_end)]
    print(f"[CohortBuilder] After date/toxic filter: {len(df)} records")

    # Compute correction freq (vectorized)
    print("[CohortBuilder] Computing correction frequencies...")
    df["correction_freq"] = _correction_freq_vectorized(df["conversation"].tolist())

    # Compute prompt tokens
    print("[CohortBuilder] Tokenizing first user turns...")
    first_turns = _first_user_content(df["conversation"].tolist())
    # Batch tokenize
    df["prompt_tokens"] = [len(enc.encode(t, disallowed_special=())) for t in first_turns]

    # Funnel step 1: unique IPs
    all_ips = df["hashed_ip"].nunique()

    # Count distinct months per IP
    ip_month_counts = df.groupby("hashed_ip")["month"].nunique()
    returning_ips = set(ip_month_counts[ip_month_counts >= min_bins].index)
    print(f"[CohortBuilder] Total IPs: {all_ips}, >=3-bin IPs: {len(returning_ips)}")

    # Filter to returning users
    df_ret = df[df["hashed_ip"].isin(returning_ips)]

    # Monthly aggregation: mean across all records per month; cohort_size = unique IPs per month bin
    monthly_tokens = df_ret.groupby("month")["prompt_tokens"].mean()
    monthly_corr = df_ret.groupby("month")["correction_freq"].mean()
    monthly_size = df_ret.groupby("month")["hashed_ip"].nunique()

    monthly = pd.DataFrame({
        "month": monthly_tokens.index,
        "prompt_tokens_mean": monthly_tokens.values,
        "correction_freq_mean": monthly_corr.values,
        "cohort_size": monthly_size.values,
    })

    # Drop bins below min_cohort_size
    monthly = monthly[monthly["cohort_size"] >= min_cohort_size].reset_index(drop=True)
    monthly = monthly.sort_values("month").reset_index(drop=True)
    print(f"[CohortBuilder] Monthly bins after size filter: {len(monthly)}")

    funnel = {
        "total_ips": int(all_ips),
        "ips_ge1_bin": int(all_ips),
        "ips_ge3_bins": len(returning_ips),
        "analysis_cohort_size": len(returning_ips),
    }
    return monthly, funnel


def build_lmsys_monthly(
    df: pd.DataFrame,
    top_n_pairs: int = 5,
    min_votes: int = 100,
    date_start: str = "2023-01",
    date_end: str = "2024-12",
) -> pd.DataFrame:
    df = df[(df["month"] >= date_start) & (df["month"] <= date_end)].copy()
    df["winner"] = df["winner"].replace("tie (bothbad)", "tie")
    df = df[df["winner"].isin(["model_a", "model_b", "tie"])]

    df["model_pair"] = df.apply(
        lambda r: "_vs_".join(sorted([str(r["model_a"]), str(r["model_b"])])), axis=1
    )

    pair_counts = df.groupby("model_pair").size()
    top_pairs = pair_counts.nlargest(top_n_pairs).index.tolist()
    df = df[df["model_pair"].isin(top_pairs)]

    df = df.copy()
    df["is_win"] = (df["winner"] == "model_a").astype(int)
    df["is_lose"] = (df["winner"] == "model_b").astype(int)
    df["is_tie"] = (df["winner"] == "tie").astype(int)

    monthly = df.groupby(["month", "model_pair"]).agg(
        win_count=("is_win", "sum"),
        lose_count=("is_lose", "sum"),
        tie_count=("is_tie", "sum"),
    ).reset_index()

    monthly["total"] = monthly["win_count"] + monthly["lose_count"] + monthly["tie_count"]
    monthly = monthly[monthly["total"] >= min_votes].drop(columns="total")
    return monthly
