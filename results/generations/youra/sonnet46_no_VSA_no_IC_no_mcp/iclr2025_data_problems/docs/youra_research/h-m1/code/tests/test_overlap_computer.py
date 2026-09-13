"""Tests for overlap_computer.py — A-5."""
import json
import sys
import tempfile
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).parent.parent))

from overlap_computer import (
    _compute_single, compute_overlap_batch,
    save_overlap_checkpoint, load_overlap_checkpoint,
)
from sampler import DocWithMeta


def _make_docs(texts: list[str], is_removed: bool = True) -> list[DocWithMeta]:
    return [DocWithMeta(text=t, doc_id=str(i), pile_subset="test", is_removed=is_removed)
            for i, t in enumerate(texts)]


def test_compute_single_basic():
    text = "hello world this is a test sentence"
    # 13-gram set containing a substring of text
    ngram = text[0:13]
    ngram_sets = [("bench", [ngram, "not_in_text"])]
    result = _compute_single((text, ngram_sets, 13))
    assert "bench" in result
    assert 0.0 <= result["bench"] <= 1.0
    assert result["bench"] > 0.0  # ngram IS in doc


def test_compute_single_empty_text():
    result = _compute_single(("", [("b", ["abc"])], 13))
    assert result["b"] == 0.0


def test_compute_single_no_overlap():
    text = "a" * 20
    ngram_sets = [("b", ["z" * 13])]
    result = _compute_single((text, ngram_sets, 13))
    assert result["b"] == 0.0


def test_compute_overlap_batch_shape():
    texts = ["hello world this is a test " * 3, "another document text here " * 3]
    docs = _make_docs(texts)
    ngram_sets = {"bench1": frozenset(["hello world this "]), "bench2": frozenset()}
    arr = compute_overlap_batch(docs, ngram_sets, n=13, n_workers=1)
    assert arr.shape == (2, 2)  # [n_docs, n_benchmarks]
    assert arr.dtype == np.float32


def test_overlap_checkpoint_roundtrip():
    with tempfile.TemporaryDirectory() as td:
        ckpt = Path(td) / "overlaps.json"
        r_arr = np.array([[0.1, 0.2], [0.3, 0.4]], dtype=np.float32)
        t_arr = np.array([[0.05, 0.1]], dtype=np.float32)
        benchmarks = ["mmlu", "hellaswag"]
        save_overlap_checkpoint(r_arr, t_arr, benchmarks, ckpt)
        loaded = load_overlap_checkpoint(ckpt)
        assert loaded is not None
        r_loaded, t_loaded, bm_loaded = loaded
        assert bm_loaded == benchmarks
        np.testing.assert_allclose(r_loaded, r_arr, rtol=1e-5)
        np.testing.assert_allclose(t_loaded, t_arr, rtol=1e-5)


def test_load_missing_overlap_checkpoint():
    result = load_overlap_checkpoint(Path("/nonexistent/overlaps.json"))
    assert result is None
