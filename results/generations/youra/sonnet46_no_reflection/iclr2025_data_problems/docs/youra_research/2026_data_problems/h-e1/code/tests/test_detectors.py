"""Tests for detector families — spec compliance."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from config import ExperimentConfig
from index_builder import NgramIndex
from detectors.ngram_detector import NgramDetector
from detectors.embedding_detector import EmbeddingDetector
from detectors.constat_detector import ConStatDetector


def _make_cfg():
    return ExperimentConfig()


class MockSBERTIndex:
    """Mock SBERT index for testing without GPU."""
    def search(self, texts, k=1):
        N = len(texts)
        distances = np.random.rand(N, k).astype(np.float32)
        indices = np.zeros((N, k), dtype=np.int64)
        return distances, indices


def test_ngram_detector_predict_shape():
    cfg = _make_cfg()
    det = NgramDetector(cfg)
    ngram_set = {"hello world foo", "quick brown fox"}
    idx = NgramIndex(ngram_set, n=3)
    texts = ["hello world foo bar", "something else entirely", "quick brown fox test"]
    preds = det.predict(texts, idx)
    assert preds.shape == (3,)
    assert preds.dtype == np.int64
    assert set(preds).issubset({0, 1})


def test_ngram_detector_score_shape():
    cfg = _make_cfg()
    det = NgramDetector(cfg)
    ngram_set = {"hello world foo"}
    idx = NgramIndex(ngram_set, n=3)
    texts = ["hello world foo bar"]
    scores = det.score(texts, idx)
    assert scores.shape == (1,)
    assert scores.dtype == np.int64


def test_embedding_detector_predict_shape():
    cfg = _make_cfg()
    det = EmbeddingDetector(cfg)
    mock_idx = MockSBERTIndex()
    texts = ["text one", "text two", "text three"]
    preds = det.predict(texts, mock_idx)
    assert preds.shape == (3,)
    assert preds.dtype == np.int64
    assert set(preds).issubset({0, 1})


def test_embedding_detector_score_shape():
    cfg = _make_cfg()
    det = EmbeddingDetector(cfg)
    mock_idx = MockSBERTIndex()
    texts = ["text one", "text two"]
    scores = det.score(texts, mock_idx)
    assert scores.shape == (2,)
    assert scores.dtype == np.float32


def test_constat_detector_predict_shape():
    cfg = _make_cfg()
    det = ConStatDetector(cfg)
    texts = ["short text", "a much longer text with many words " * 10]
    preds = det.predict(texts)
    assert preds.shape == (2,)
    assert preds.dtype == np.int64
    assert set(preds).issubset({0, 1})


def test_detector_registry_has_five_detectors():
    from detectors import get_detector_registry
    cfg = _make_cfg()
    registry = get_detector_registry(cfg)
    assert len(registry) == 5
    assert "ngram" in registry
    assert "embedding" in registry
    assert "minkpp" in registry
    assert "dcpdd" in registry
    assert "constat" in registry
