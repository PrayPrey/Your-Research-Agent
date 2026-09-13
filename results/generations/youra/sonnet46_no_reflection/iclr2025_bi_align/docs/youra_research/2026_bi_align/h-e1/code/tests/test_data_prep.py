"""Tests for data_prep.py — spec compliance."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import pytest

from data_prep import (
    AIFS_PATTERNS, COSINE_THRESHOLD, MIN_TOKEN_COUNT, MODEL_NAME,
    compute_aifs_score, extract_dialogue, filter_pairs, validate_clusters,
    build_pairs_df,
)


def test_aifs_patterns_have_4_keys():
    assert len(AIFS_PATTERNS) == 4
    assert set(AIFS_PATTERNS.keys()) == {
        "structured_list", "safety_preface", "cot_marker", "hedging"
    }


def test_cosine_threshold_value():
    assert COSINE_THRESHOLD == 0.85


def test_min_token_count():
    assert MIN_TOKEN_COUNT == 20


def test_model_name():
    assert "all-MiniLM-L6-v2" in MODEL_NAME


def test_compute_aifs_score_returns_float():
    score = compute_aifs_score("This is a simple sentence.")
    assert isinstance(score, float)
    assert score >= 0.0


def test_compute_aifs_score_structured_list():
    text = "1. First item\n2. Second item\n3. Third item"
    score = compute_aifs_score(text)
    assert score > 0.0


def test_compute_aifs_score_empty_like():
    score = compute_aifs_score("word")
    assert score >= 0.0


def test_extract_dialogue_strips_prefix():
    chosen = "Human: hello\n\nAssistant: Hi there!"
    rejected = "Human: hello\n\nAssistant: Hey!"
    result = extract_dialogue({"chosen": chosen, "rejected": rejected})
    assert "chosen" in result
    assert "rejected" in result
    assert "prompt" in result
    assert result["chosen"] != chosen  # prefix stripped
    assert result["rejected"] != rejected


def test_filter_pairs_removes_short():
    df = pd.DataFrame({
        "chosen": ["word " * 25, "word"],
        "rejected": ["word " * 25, "word " * 25],
    })
    result = filter_pairs(df)
    assert len(result) == 1


def test_filter_pairs_keeps_long():
    df = pd.DataFrame({
        "chosen": ["word " * 25],
        "rejected": ["word " * 25],
    })
    result = filter_pairs(df)
    assert len(result) == 1


def test_validate_clusters_raises_on_few():
    df = pd.DataFrame({
        "cluster_id": [0] * 10,
        "chosen": [1] * 10,
    })
    with pytest.raises(ValueError, match="valid clusters"):
        validate_clusters(df)


def test_validate_clusters_passes_with_enough():
    # 110 clusters each with 4 rows (= 2 pairs, since validate_clusters uses row_count // 2)
    cluster_ids = []
    for i in range(110):
        cluster_ids.extend([i, i, i, i])
    df = pd.DataFrame({
        "cluster_id": cluster_ids,
        "chosen": [1] * len(cluster_ids),
    })
    validate_clusters(df)  # should not raise


def test_build_pairs_df_columns():
    df_base = pd.DataFrame({
        "chosen": ["word " * 25] * 5,
        "rejected": ["text " * 25] * 5,
    })
    df_online = pd.DataFrame({
        "chosen": ["word " * 25] * 5,
        "rejected": ["text " * 25] * 5,
    })
    cluster_ids = np.array([0, 0, 1, 1, 2, 0, 0, 1, 1, 2])
    df_pairs = build_pairs_df(df_base, df_online, cluster_ids)
    required_cols = {"chosen", "delta_aifs", "delta_length", "delta_aifs_x_split", "split", "cluster_id"}
    assert required_cols.issubset(set(df_pairs.columns))


def test_build_pairs_df_interaction_column():
    df_base = pd.DataFrame({
        "chosen": ["word " * 25] * 3,
        "rejected": ["text " * 25] * 3,
    })
    df_online = pd.DataFrame({
        "chosen": ["word " * 25] * 3,
        "rejected": ["text " * 25] * 3,
    })
    cluster_ids = np.array([0, 0, 1, 0, 0, 1])
    df_pairs = build_pairs_df(df_base, df_online, cluster_ids)
    # delta_aifs_x_split = delta_aifs * split
    for _, row in df_pairs.iterrows():
        assert abs(row["delta_aifs_x_split"] - row["delta_aifs"] * row["split"]) < 1e-9


def test_build_pairs_df_split_labels():
    df_base = pd.DataFrame({
        "chosen": ["word " * 25] * 3,
        "rejected": ["text " * 25] * 3,
    })
    df_online = pd.DataFrame({
        "chosen": ["word " * 25] * 3,
        "rejected": ["text " * 25] * 3,
    })
    cluster_ids = np.array([0, 0, 1, 0, 0, 1])
    df_pairs = build_pairs_df(df_base, df_online, cluster_ids)
    assert set(df_pairs["split"].unique()).issubset({0, 1})
