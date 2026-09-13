"""Tests for prepare_data.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pytest
from datasets import Dataset

from prepare_data import (
    DEDUP_THRESHOLD,
    TARGET_PROBLEMS,
    UNIFORM_TEMPLATE,
    build_equal_mix,
    count_dataset_tokens,
    embed_texts,
    format_example,
    repeat_to_token_budget,
)


def make_ds(texts):
    return Dataset.from_dict({"text": texts})


def test_format_example_humaneval():
    ex = {
        "prompt": 'def add(a, b):\n    """Add two numbers."""\n',
        "canonical_solution": "    return a + b\n",
    }
    result = format_example(ex, "humaneval")
    assert "text" in result
    assert "Add two numbers" in result["text"]
    assert "return a + b" in result["text"]


def test_format_example_mbpp():
    ex = {"text": "Write a function to add two numbers.", "code": "def add(a, b):\n    return a + b"}
    result = format_example(ex, "mbpp")
    assert "text" in result
    assert "add two numbers" in result["text"].lower()


def test_format_example_leetcode():
    ex = {"description": "Two Sum problem.", "python_solution": "def twoSum(nums, target):\n    pass"}
    result = format_example(ex, "leetcode")
    assert "twoSum" in result["text"]


def test_build_equal_mix():
    datasets_by_source = {
        "humaneval_only": make_ds([f"text_{i}" for i in range(50)]),
        "mbpp_only": make_ds([f"mbpp_{i}" for i in range(50)]),
        "leetcode_only": make_ds([f"lc_{i}" for i in range(50)]),
    }
    mixed = build_equal_mix(datasets_by_source)
    assert len(mixed) == 123  # 41 * 3
    texts = mixed["text"]
    # Should have examples from all sources
    has_text = any("text_" in t for t in texts)
    has_mbpp = any("mbpp_" in t for t in texts)
    has_lc = any("lc_" in t for t in texts)
    assert has_text and has_mbpp and has_lc


def test_repeat_to_token_budget():
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        "deepseek-ai/deepseek-coder-1.3b-base", trust_remote_code=True
    )
    ds = make_ds(["def add(a, b): return a + b"] * 5)
    token_count = count_dataset_tokens(ds, tokenizer)
    target = token_count * 3
    result = repeat_to_token_budget(ds, target, tokenizer)
    actual = count_dataset_tokens(result, tokenizer)
    assert actual <= target
    assert actual >= token_count  # at least 1 epoch


def test_embed_texts_shape():
    embs = embed_texts(["hello world", "test function"])
    assert embs.shape == (2, 384)
    # L2-normalized
    norms = np.linalg.norm(embs, axis=1)
    np.testing.assert_allclose(norms, 1.0, atol=1e-5)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
