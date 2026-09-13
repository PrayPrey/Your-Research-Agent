"""Tests for geometry_features.py — spec compliance."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from config import ExperimentConfig
from geometry_features import GeometryStratifier


def test_compute_thresholds_returns_two_floats():
    cfg = ExperimentConfig()
    strat = GeometryStratifier(cfg)
    ngram_counts = np.array([0, 1, 2, 5, 10, 0, 3, 7, 1, 2], dtype=np.int64)
    cosines = np.array([0.1, 0.3, 0.5, 0.7, 0.9, 0.2, 0.4, 0.8, 0.6, 0.95], dtype=np.float32)
    lex_t, sem_t = strat.compute_thresholds(ngram_counts, cosines)
    assert isinstance(lex_t, float)
    assert isinstance(sem_t, float)


def test_assign_strata_only_valid_labels():
    cfg = ExperimentConfig()
    strat = GeometryStratifier(cfg)
    ngram_counts = np.array([10, 0, 0, 5, 0], dtype=np.int64)
    cosines = np.array([0.1, 0.9, 0.2, 0.5, 0.8], dtype=np.float32)
    strata = strat.assign_strata(ngram_counts, cosines, lexical_thresh=5.0, semantic_thresh=0.75)
    valid = {"lexical", "semantic", "indeterminate"}
    assert set(np.unique(strata)).issubset(valid)


def test_assign_strata_lexical_items():
    cfg = ExperimentConfig()
    strat = GeometryStratifier(cfg)
    ngram_counts = np.array([10, 0, 0], dtype=np.int64)
    cosines = np.array([0.1, 0.9, 0.5], dtype=np.float32)
    strata = strat.assign_strata(ngram_counts, cosines, lexical_thresh=5.0, semantic_thresh=0.75)
    assert strata[0] == "lexical"
    assert strata[1] == "semantic"
    assert strata[2] == "indeterminate"


def test_assign_strata_lexical_overrides_semantic():
    cfg = ExperimentConfig()
    strat = GeometryStratifier(cfg)
    ngram_counts = np.array([10], dtype=np.int64)
    cosines = np.array([0.9], dtype=np.float32)
    strata = strat.assign_strata(ngram_counts, cosines, lexical_thresh=5.0, semantic_thresh=0.75)
    assert strata[0] == "lexical"
