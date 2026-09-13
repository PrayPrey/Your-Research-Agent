"""Tests for index_builder.py — spec compliance."""
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from config import ExperimentConfig
from index_builder import NgramIndex, NgramIndexBuilder, _ngrams


def test_ngrams_returns_list():
    grams = _ngrams("the quick brown fox jumps over the lazy dog", 3)
    assert isinstance(grams, list)
    assert len(grams) > 0


def test_ngram_index_max_overlap_returns_int():
    ngram_set = {"the quick brown", "quick brown fox"}
    idx = NgramIndex(ngram_set, n=3)
    result = idx.max_overlap("the quick brown fox", n=3)
    assert isinstance(result, int)
    assert result >= 0


def test_ngram_index_max_overlap_zero_no_match():
    ngram_set = {"hello world foo"}
    idx = NgramIndex(ngram_set, n=3)
    result = idx.max_overlap("completely different text here", n=3)
    assert result == 0


def test_ngram_index_is_contaminated():
    ngram_set = {"the quick brown"}
    idx = NgramIndex(ngram_set, n=3)
    assert idx.is_contaminated("the quick brown fox jumps", threshold=1)
    assert not idx.is_contaminated("hello world test completely different", threshold=1)


def test_ngram_build_and_load():
    with tempfile.TemporaryDirectory() as tmpdir:
        cfg = ExperimentConfig()
        cfg.index_dir = tmpdir
        cfg.ngram_n = 3
        builder = NgramIndexBuilder(cfg)
        texts = iter(["hello world foo bar", "quick brown fox", "the lazy dog"])
        builder.build_index("test_corpus", texts)
        idx = builder.load_index("test_corpus")
        assert isinstance(idx, NgramIndex)
        result = idx.max_overlap("hello world foo", n=3)
        assert result >= 0
