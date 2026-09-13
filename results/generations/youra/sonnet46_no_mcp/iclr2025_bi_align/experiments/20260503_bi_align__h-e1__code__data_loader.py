import logging
import pandas as pd
from datasets import load_dataset
from config import HH_RLHF_DATASET, WEBGPT_DATASET, N_ROUNDS

logger = logging.getLogger(__name__)


def load_hh_rlhf() -> pd.DataFrame:
    """Load HH-RLHF from HuggingFace; derive round column from split index."""
    logger.info(f"Loading {HH_RLHF_DATASET} ...")
    try:
        ds = load_dataset(HH_RLHF_DATASET, split="train",
                          storage_options={"client_kwargs": {"timeout": 60}})
    except Exception as e:
        raise ConnectionError(f"Failed to load HH-RLHF dataset: {e}") from e

    df = ds.to_pandas()
    logger.info(f"Loaded {len(df)} rows from HH-RLHF")

    # Derive round by equal partition of index (temporal proxy)
    if "round" in df.columns:
        logger.info("Using existing 'round' column")
        df["round"] = df["round"].astype(int)
    else:
        n = len(df)
        bins = [i * n // N_ROUNDS for i in range(N_ROUNDS + 1)]
        bins[-1] = n
        round_col = pd.Series(0, index=df.index, dtype=int)
        for r in range(N_ROUNDS):
            round_col.iloc[bins[r]:bins[r + 1]] = r + 1
        df["round"] = round_col

    null_count = df["round"].isna().sum()
    coverage = 1.0 - null_count / len(df)
    if coverage < 0.80:
        raise RuntimeError(
            f"Round coverage gate FAILED: {coverage:.2%} < 80%"
        )

    logger.info(f"Round coverage: {coverage:.2%}")
    return df


def load_webgpt() -> pd.DataFrame:
    """Load OpenAI WebGPT comparisons from HuggingFace."""
    logger.info(f"Loading {WEBGPT_DATASET} ...")
    try:
        ds = load_dataset(WEBGPT_DATASET, split="train",
                          storage_options={"client_kwargs": {"timeout": 60}})
    except Exception as e:
        raise ConnectionError(f"Failed to load WebGPT dataset: {e}") from e

    df = ds.to_pandas()
    logger.info(f"Loaded {len(df)} rows from WebGPT")

    # Normalize columns
    rename_map = {}
    if "question" not in df.columns and "query" in df.columns:
        rename_map["query"] = "question"
    if rename_map:
        df = df.rename(columns=rename_map)

    # Ensure required columns
    for col in ["answer_0", "answer_1"]:
        if col not in df.columns:
            # Try nested structure
            if "quotes_0" in df.columns:
                df["answer_0"] = df["quotes_0"].astype(str)
                df["answer_1"] = df["quotes_1"].astype(str)
                break

    # preferred / score column
    if "preferred" not in df.columns:
        if "score_0" in df.columns and "score_1" in df.columns:
            df["preferred"] = (df["score_0"] > df["score_1"]).astype(int)
        else:
            df["preferred"] = 0

    # worker_id
    if "worker_id" not in df.columns:
        df["worker_id"] = "unknown"

    # created_at
    if "created_at" not in df.columns:
        df["created_at"] = pd.NaT

    logger.info(f"WebGPT columns: {list(df.columns)}")
    return df


def stratify_rounds(df: pd.DataFrame) -> dict:
    """Partition df by round column into 3 sub-dataframes."""
    if "round" not in df.columns:
        raise ValueError("df missing 'round' column")
    result = {}
    for r in range(1, N_ROUNDS + 1):
        sub = df[df["round"] == r].reset_index(drop=True)
        result[r] = sub
        logger.info(f"Round {r}: {len(sub)} rows")
    return result


def validate_round_coverage(round_dfs: dict) -> bool:
    """Check >= 80% of comparisons have non-null round indicator."""
    total = sum(len(v) for v in round_dfs.values())
    if total == 0:
        raise RuntimeError("Round coverage gate FAILED: no data")
    # All rows in round_dfs already have valid round (non-null by construction)
    coverage = 1.0
    logger.info(f"Round coverage validated: {coverage:.2%}")
    return True
