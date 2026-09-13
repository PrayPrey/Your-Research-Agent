"""Spec compliance tests for matrix.py (standardize_model_name + build_matrix)."""
import math
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from code.matrix import standardize_model_name, build_matrix
from code.config import REQUIRED_COLS, SOURCE_PRIORITY


def test_standardize_known_names():
    assert standardize_model_name("llama-2-7b") == "LLaMA-2-7B"
    assert standardize_model_name("LLAMA-2-7B") == "LLaMA-2-7B"
    assert standardize_model_name("  llama-2-7b  ") == "LLaMA-2-7B"
    assert standardize_model_name("gpt-3.5-turbo") == "GPT-3.5-Turbo"
    assert standardize_model_name("GPT-4") == "GPT-4"
    assert standardize_model_name("mistral-7b-instruct") == "Mistral-7B-Instruct"


def test_standardize_unknown_returns_stripped():
    result = standardize_model_name("unknown-model-xyz")
    assert result == "unknown-model-xyz"


def test_build_matrix_source_priority():
    score_dicts = {
        "TrustLLM": {"ModelA": {"BBQ-Disambig": 0.8}},
        "DecodingTrust": {"ModelA": {"BBQ-Disambig": 0.6}},  # should be overridden
    }
    matrix_df, attribution_df = build_matrix(score_dicts)
    assert matrix_df.loc["ModelA", "BBQ-Disambig"] == pytest.approx(0.8)
    assert attribution_df.loc["ModelA", "BBQ-Disambig"] == "TrustLLM"


def test_build_matrix_nan_for_missing():
    score_dicts = {"TrustLLM": {"ModelA": {"BBQ-Disambig": 0.7}}}
    matrix_df, _ = build_matrix(score_dicts)
    assert math.isnan(matrix_df.loc["ModelA", "BBQ-Ambig"])
    assert math.isnan(matrix_df.loc["ModelA", "MMLU"])


def test_build_matrix_columns():
    score_dicts = {"TrustLLM": {"M1": {"BBQ-Disambig": 0.5}}}
    matrix_df, attribution_df = build_matrix(score_dicts)
    assert list(matrix_df.columns) == REQUIRED_COLS
    assert list(attribution_df.columns) == REQUIRED_COLS


def test_build_matrix_multiple_models():
    score_dicts = {
        "TrustLLM": {
            "LLaMA-2-7B": {"BBQ-Disambig": 0.75, "ANLI-R1": 0.55},
            "GPT-4": {"BBQ-Disambig": 0.90, "MMLU": 0.86},
        }
    }
    matrix_df, _ = build_matrix(score_dicts)
    assert len(matrix_df) == 2
    assert matrix_df.loc["GPT-4", "MMLU"] == pytest.approx(0.86)
    assert math.isnan(matrix_df.loc["LLaMA-2-7B", "MMLU"])
