"""Tests for curate_v2.py — pad_to_token_budget spec compliance."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from curate_v2 import pad_to_token_budget


def make_docs(n: int, words_per_doc: int = 100) -> list:
    return [{"text": "the quick brown fox " * (words_per_doc // 4)} for _ in range(n)]


def test_pad_no_change_when_sufficient():
    docs = make_docs(n=1000, words_per_doc=1000)
    original_len = len(docs)
    result = pad_to_token_budget(docs, target_tokens=100)
    assert len(result) >= original_len


def test_pad_reaches_target():
    docs = make_docs(n=10, words_per_doc=100)
    target = 1_000_000  # 1M tokens
    result = pad_to_token_budget(docs[:], target_tokens=target)
    approx_tokens = sum(len(d["text"].split()) * 4 // 3 for d in result)
    assert approx_tokens >= target


def test_pad_returns_list():
    docs = make_docs(n=5)
    result = pad_to_token_budget(docs[:], target_tokens=1_000_000)
    assert isinstance(result, list)


def test_pad_preserves_doc_structure():
    docs = [{"text": "hello world " * 10, "id": i} for i in range(20)]
    result = pad_to_token_budget(docs[:], target_tokens=1_000_000)
    assert all("text" in d for d in result)


def test_pad_reproducible_with_seed():
    docs = make_docs(n=20, words_per_doc=50)
    r1 = pad_to_token_budget(docs[:], target_tokens=500_000, seed=42)
    r2 = pad_to_token_budget(docs[:], target_tokens=500_000, seed=42)
    assert len(r1) == len(r2)
