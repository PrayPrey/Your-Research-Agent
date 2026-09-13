"""
Data collection module for H-E1.
Handles Open LLM Leaderboard loading, deduplication, filtering, and model card retrieval.
"""
import os
import sys
CODE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CODE_DIR)

import pandas as pd
import numpy as np
from typing import Optional

import config
import utils

# Track funnel counts for dropout visualization
_funnel_counts = {}

# Dropout log path
DROPOUT_LOG = os.path.join(config.DATA_DIR, 'dropout_log.csv')


def load_leaderboard() -> pd.DataFrame:
    """Load Open LLM Leaderboard v2 via datasets.load_dataset (open-llm-leaderboard/contents).

    Returns: DataFrame with columns [model_name, avg_score] + BENCHMARK_COLS (normalized),
             shape (~4000-5000, 8).
    """
    from datasets import load_dataset

    print("[load_leaderboard] Loading Open LLM Leaderboard v2 (contents)...")
    dataset = load_dataset(config.LEADERBOARD_DATASET, split="train")
    df = dataset.to_pandas()

    print(f"[load_leaderboard] Loaded {len(df)} rows, columns: {list(df.columns)[:10]}")

    # v2 uses 'fullname' as the model identifier
    model_col = None
    for candidate in ['fullname', 'model_name_for_query', 'model_name', 'model', 'Model']:
        if candidate in df.columns:
            model_col = candidate
            break

    if model_col is None:
        raise ValueError(f"Cannot find model name column. Available: {list(df.columns)}")

    df = df.rename(columns={model_col: 'model_name'})

    # Map v2 benchmark columns to normalized names
    col_mappings = {
        'IFEval': 'ifeval',
        'BBH': 'bbh',
        'MATH Lvl 5': 'math_lvl5',
        'GPQA': 'gpqa',
        'MUSR': 'musr',
        'MMLU-PRO': 'mmlu_pro',
        'Average \u2b06\ufe0f': 'avg_score',  # Average ⬆️
        '#Params (B)': 'params_b',
        'Architecture': 'arch_raw',
    }
    df = df.rename(columns={k: v for k, v in col_mappings.items() if k in df.columns})

    # Keep relevant columns
    keep_cols = ['model_name', 'avg_score', 'params_b', 'arch_raw'] + \
                [c for c in config.BENCHMARK_COLS if c in df.columns]
    df = df[[c for c in keep_cols if c in df.columns]]

    # Convert numeric columns
    for col in ['avg_score', 'params_b'] + [c for c in config.BENCHMARK_COLS if c in df.columns]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    _funnel_counts['raw'] = len(df)
    print(f"[load_leaderboard] After column mapping: {len(df)} rows, {len(df.columns)} columns")
    return df


def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    """Keep latest evaluation per model_name (sort by index desc, drop_duplicates).

    Returns: deduplicated DataFrame, shape (~N_unique, 7).
    """
    # If there's a date/submission column, sort by it desc
    date_cols = [c for c in df.columns if 'date' in c.lower() or 'time' in c.lower() or 'submit' in c.lower()]

    if date_cols:
        df_sorted = df.sort_values(date_cols[0], ascending=False)
    else:
        # Keep last occurrence (assumes later rows are newer)
        df_sorted = df

    dedup_df = df_sorted.drop_duplicates(subset=['model_name'], keep='first')
    dedup_df = dedup_df.reset_index(drop=True)

    _funnel_counts['after_dedup'] = len(dedup_df)
    print(f"[deduplicate] {len(df)} -> {len(dedup_df)} unique models")
    return dedup_df


def filter_benchmark_coverage(
    df: pd.DataFrame,
    min_benchmarks: int = 4,
) -> pd.DataFrame:
    """Keep rows where count(non-null BENCHMARK_COLS) >= min_benchmarks.

    Returns: filtered DataFrame, shape (~1000-2000, 7).
    """
    benchmark_cols = [c for c in config.BENCHMARK_COLS if c in df.columns]

    if not benchmark_cols:
        print("[filter_benchmark_coverage] WARNING: No benchmark columns found")
        return df

    # Count non-null benchmark values per row
    non_null_counts = df[benchmark_cols].notna().sum(axis=1)
    mask = non_null_counts >= min_benchmarks
    filtered_df = df[mask].reset_index(drop=True)

    _funnel_counts['after_benchmark_filter'] = len(filtered_df)
    print(f"[filter_benchmark_coverage] {len(df)} -> {len(filtered_df)} models with >={min_benchmarks} benchmarks")
    return filtered_df


def retrieve_model_cards(
    model_ids: list,
    checkpoint_dir: str,
    max_retries: int = 5,
    base_delay: float = 2.0,
) -> dict:
    """Retrieve HF model cards + model_info for each model_id.

    Returns accessible subset as dict: {model_id: {"card_text": str, "model_info": object}}
    Checkpoints every CHECKPOINT_INTERVAL models.
    Resumes from checkpoint if available.
    """
    from huggingface_hub import ModelCard, HfApi

    os.makedirs(checkpoint_dir, exist_ok=True)
    checkpoint_path = os.path.join(checkpoint_dir, 'cards.json')
    dropout_log_path = DROPOUT_LOG

    # Step 1: Load existing checkpoint
    existing = utils.load_checkpoint(checkpoint_path)
    # existing is a dict {model_id: record}
    if not isinstance(existing, dict):
        existing = {}

    # Step 2: Determine remaining models to process
    remaining = [m for m in model_ids if m not in existing]
    results = dict(existing)

    print(f"[retrieve_model_cards] {len(existing)} cached, {len(remaining)} remaining")

    api = HfApi()

    # Step 3: Process remaining models
    for i, model_id in enumerate(remaining):
        try:
            card = utils.exponential_backoff(
                ModelCard.load, model_id,
                max_retries=max_retries,
                base_delay=base_delay
            )
            info = utils.exponential_backoff(
                api.model_info, model_id,
                max_retries=max_retries,
                base_delay=base_delay
            )
            results[model_id] = {
                "card_text": card.content if hasattr(card, 'content') else str(card),
                "model_info": info
            }
        except Exception as e:
            utils.log_dropout(model_id, "card_retrieval", str(e)[:200], dropout_log_path)
            continue

        # Checkpoint every CHECKPOINT_INTERVAL models
        if (i + 1) % config.CHECKPOINT_INTERVAL == 0:
            # Save as list of records with model_id included
            records = [{"model_id": k, **v} for k, v in results.items() if isinstance(v, dict) and "card_text" in v]
            utils.save_checkpoint(records, checkpoint_path)
            utils.print_progress("card_retrieval", len(results), len(model_ids))

    # Final save
    records = [{"model_id": k, **{kk: str(vv) for kk, vv in v.items()}} if isinstance(v, dict) else {"model_id": k}
               for k, v in results.items()]
    utils.save_checkpoint(records, checkpoint_path)

    _funnel_counts['cards_retrieved'] = len(results)
    print(f"[retrieve_model_cards] Retrieved {len(results)} model cards")
    return results
