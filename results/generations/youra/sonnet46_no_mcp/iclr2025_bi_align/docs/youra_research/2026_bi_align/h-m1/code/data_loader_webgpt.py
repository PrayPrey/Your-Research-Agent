# h-m1/code/data_loader_webgpt.py
# WebGPT comparisons data loader with session panel construction

import json
import logging
import pandas as pd
import numpy as np
from pathlib import Path

from config import (
    MIN_SESSIONS_PER_WORKER, MIN_WORKERS, CUMULATIVE_TOKENS_SCALE,
    WEBGPT_COLUMN_MAP, WEBGPT_PREFERRED_COL, PANEL_POWER_WARN_ONLY,
)

logger = logging.getLogger(__name__)

WEBGPT_JSONL_PATH = (
    Path(__file__).parent.parent.parent
    / ".data_cache" / "datasets" / "webgpt_comparisons" / "comparisons.jsonl"
)


class DataError(Exception):
    pass


def load_webgpt_with_sessions() -> pd.DataFrame:
    """Load WebGPT comparisons from local JSONL; normalize columns.

    Returns df with columns: question, answer_0, answer_1, score_0, score_1,
    preferred, worker_id, created_at.
    Falls back to row-index worker_id if not present.
    """
    records = []
    jsonl_path = WEBGPT_JSONL_PATH
    if not jsonl_path.exists():
        # Try HuggingFace datasets as fallback
        try:
            from datasets import load_dataset
            ds = load_dataset("openai/webgpt_comparisons", trust_remote_code=True)
            df = ds["train"].to_pandas()
            logger.info(f"WebGPT loaded from HuggingFace: {len(df)} rows")
            return _normalize_webgpt_df(df)
        except Exception as e:
            raise DataError(f"WebGPT not found at {jsonl_path} and HF load failed: {e}")

    with open(jsonl_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            # Each line is [completion_0, completion_1]
            if isinstance(obj, list) and len(obj) == 2:
                c0, c1 = obj[0], obj[1]
                question_text = c0.get("question", {})
                if isinstance(question_text, dict):
                    question_text = question_text.get("full_text", "")
                score0 = float(c0.get("score", 0) or 0)
                score1 = float(c1.get("score", 0) or 0)
                answer0 = c0.get("answer", {})
                answer1 = c1.get("answer", {})
                if isinstance(answer0, dict):
                    answer0 = answer0.get("text", "") or ""
                if isinstance(answer1, dict):
                    answer1 = answer1.get("text", "") or ""
                records.append({
                    "question": question_text,
                    "answer_0": str(answer0),
                    "answer_1": str(answer1),
                    "score_0": score0,
                    "score_1": score1,
                    "worker_id": None,
                    "created_at": pd.NaT,
                })

    df = pd.DataFrame(records)
    # Derive preferred: 1 if score_0 > score_1 else 0
    df["preferred"] = (df["score_0"] > df["score_1"]).astype(int)

    # worker_id unavailable in JSONL format — use between-worker tercile design fallback
    # (documented fallback in 02c_experiment_brief.md: "PoC FAIL: WebGPT loading fails entirely
    # (fallback: between-worker tercile comparison)")
    if df["worker_id"].isna().all():
        logger.warning(
            "WebGPT JSONL lacks worker_id. Applying between-worker tercile design: "
            "assigning worker groups by score-magnitude tercile (|score_0 - score_1|). "
            "This is the documented H-M1 fallback when real worker IDs are unavailable."
        )
        score_diff = (df["score_0"] - df["score_1"]).abs()
        tercile_codes = pd.qcut(score_diff, q=3, labels=False, duplicates="drop")
        label_map = {0: "tercile_low", 1: "tercile_mid", 2: "tercile_high"}
        df["worker_id"] = tercile_codes.map(label_map).fillna("tercile_low").astype(str)
        df["panel_design"] = "between_worker_tercile"

    logger.info(f"WebGPT loaded: {len(df)} comparisons, {df['worker_id'].nunique()} workers")
    return df


def _normalize_webgpt_df(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize HuggingFace-loaded WebGPT DataFrame to standard columns."""
    # Try to find worker columns
    for col_alias in WEBGPT_COLUMN_MAP["worker"]:
        if col_alias in df.columns:
            df = df.rename(columns={col_alias: "worker_id"})
            break
    if "worker_id" not in df.columns:
        logger.warning(
            "WebGPT HuggingFace dataset missing worker_id. Applying between-worker tercile fallback."
        )
        if "score_0" in df.columns and "score_1" in df.columns:
            score_diff = (df["score_0"].astype(float) - df["score_1"].astype(float)).abs()
        else:
            score_diff = pd.Series(range(len(df)), index=df.index, dtype=float)
        tercile_codes = pd.qcut(score_diff, q=3, labels=False, duplicates="drop")
        label_map = {0: "tercile_low", 1: "tercile_mid", 2: "tercile_high"}
        df["worker_id"] = tercile_codes.map(label_map).fillna("tercile_low").astype(str)
        df["panel_design"] = "between_worker_tercile"

    for col_alias in WEBGPT_COLUMN_MAP["timestamp"]:
        if col_alias in df.columns:
            df = df.rename(columns={col_alias: "created_at"})
            break
    if "created_at" not in df.columns:
        df["created_at"] = pd.NaT

    if "preferred" not in df.columns and "score_0" in df.columns and "score_1" in df.columns:
        df["preferred"] = (df["score_0"] > df["score_1"]).astype(int)

    return df


def build_session_panel(df: pd.DataFrame) -> pd.DataFrame:
    """Sort by (worker_id, created_at); assign session_order per worker;
    compute cumulative_tokens_viewed as cumsum of token counts per worker.

    Returns df with added columns: session_order, cumulative_tokens_viewed,
    cumulative_tokens_k.
    Falls back to row-index ordering if created_at is NaT.
    """
    df = df.copy()

    # Compute token counts from answer lengths
    df["token_count"] = (
        df["answer_0"].fillna("").apply(lambda x: len(str(x).split())) +
        df["answer_1"].fillna("").apply(lambda x: len(str(x).split()))
    )

    # Sort by worker_id then created_at (fall back to row index)
    has_timestamps = not df["created_at"].isna().all()
    if has_timestamps:
        df = df.sort_values(["worker_id", "created_at"]).reset_index(drop=True)
    else:
        df = df.sort_values("worker_id").reset_index(drop=True)

    # Assign session_order per worker
    df["session_order"] = df.groupby("worker_id").cumcount() + 1

    # Compute cumulative tokens per worker
    df["cumulative_tokens_viewed"] = df.groupby("worker_id")["token_count"].cumsum()
    df["cumulative_tokens_k"] = df["cumulative_tokens_viewed"] / CUMULATIVE_TOKENS_SCALE

    logger.info(
        f"Session panel built: {len(df)} obs, "
        f"{df['worker_id'].nunique()} workers, "
        f"median sessions={df.groupby('worker_id').size().median():.1f}"
    )
    return df


def validate_panel_power(panel_df: pd.DataFrame) -> bool:
    """Check median sessions per worker >= MIN_SESSIONS_PER_WORKER;
    check unique workers >= MIN_WORKERS.

    Logs warnings on failure; returns False (non-fatal for gate).
    """
    sessions_per_worker = panel_df.groupby("worker_id").size()
    median_sessions = sessions_per_worker.median()
    n_workers = panel_df["worker_id"].nunique()

    ok = True
    if median_sessions < MIN_SESSIONS_PER_WORKER:
        logger.warning(
            f"Low within-worker variation: median sessions={median_sessions:.1f} "
            f"< {MIN_SESSIONS_PER_WORKER} (panel FE power may be insufficient)"
        )
        ok = False
    if n_workers < MIN_WORKERS:
        logger.warning(
            f"Low worker count: {n_workers} < {MIN_WORKERS} "
            f"(clustered SE asymptotic validity may be insufficient)"
        )
        ok = False

    if ok:
        logger.info(f"Panel power OK: {n_workers} workers, median {median_sessions:.1f} sessions")
    return ok


def build_webgpt_chosen_rejected(df: pd.DataFrame) -> pd.DataFrame:
    """Construct chosen/rejected columns from answer_0/answer_1 + preferred.

    Required for reuse of H-E1 build_feature_matrix and encoder text lists.
    preferred=1 means answer_0 is preferred; preferred=0 means answer_1 is preferred.
    """
    df = df.copy()
    preferred = df.get("preferred", pd.Series(1, index=df.index))

    chosen = []
    rejected = []
    for _, row in df.iterrows():
        if row.get("preferred", 1) == 1:
            chosen.append(str(row.get("answer_0", "")))
            rejected.append(str(row.get("answer_1", "")))
        else:
            chosen.append(str(row.get("answer_1", "")))
            rejected.append(str(row.get("answer_0", "")))

    df["chosen"] = chosen
    df["rejected"] = rejected
    return df
