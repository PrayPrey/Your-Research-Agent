"""Tests for task-002: data loading."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import tempfile
import pytest
from unittest.mock import MagicMock, patch

from config import get_config
from data import load_halueval_qa, save_dataset, load_dataset_from_disk


def _make_fake_dataset(n=100):
    """Create fake HaluEval-style dataset."""
    raw = []
    for i in range(n):
        raw.append({
            "question": f"Q{i}",
            "answer": f"A{i}",
            "hallucination": "yes" if i % 2 == 0 else "no",
            "knowledge": "ctx",
        })
    return raw


def test_load_halueval_qa():
    cfg = get_config()
    cfg.n_hallucinated = 10
    cfg.n_factual = 10

    fake_raw = _make_fake_dataset(200)
    fake_split = {"data": MagicMock()}
    fake_split["data"].__iter__ = MagicMock(return_value=iter(fake_raw))
    fake_split["data"].__len__ = MagicMock(return_value=len(fake_raw))

    mock_dataset = MagicMock()
    mock_dataset.__contains__ = lambda self, key: key == "data"
    mock_dataset.__getitem__ = lambda self, key: fake_raw
    mock_dataset.keys = lambda: ["data"]

    with patch("data.load_dataset", return_value=mock_dataset):
        examples = load_halueval_qa(cfg)

    assert len(examples) == 20
    ids = [ex["id"] for ex in examples]
    assert len(set(ids)) == len(ids), "IDs should be unique"


def test_stratification():
    cfg = get_config()
    cfg.n_hallucinated = 5
    cfg.n_factual = 5

    fake_raw = _make_fake_dataset(100)
    mock_dataset = MagicMock()
    mock_dataset.__contains__ = lambda self, key: key == "data"
    mock_dataset.__getitem__ = lambda self, key: fake_raw
    mock_dataset.keys = lambda: ["data"]

    with patch("data.load_dataset", return_value=mock_dataset):
        examples = load_halueval_qa(cfg)

    n_hallucinated = sum(1 for ex in examples if ex["hallucination_label"])
    n_factual = sum(1 for ex in examples if not ex["hallucination_label"])
    assert n_hallucinated == 5
    assert n_factual == 5


def test_reproducibility():
    cfg = get_config()
    cfg.n_hallucinated = 5
    cfg.n_factual = 5
    cfg.seed = 42

    fake_raw = _make_fake_dataset(100)
    mock_dataset = MagicMock()
    mock_dataset.__contains__ = lambda self, key: key == "data"
    mock_dataset.__getitem__ = lambda self, key: fake_raw
    mock_dataset.keys = lambda: ["data"]

    with patch("data.load_dataset", return_value=mock_dataset):
        examples1 = load_halueval_qa(cfg)
    with patch("data.load_dataset", return_value=mock_dataset):
        examples2 = load_halueval_qa(cfg)

    assert [ex["id"] for ex in examples1] == [ex["id"] for ex in examples2]


def test_save_and_load():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name

    examples = [{"id": 0, "question": "Q", "answer": "A", "hallucination_label": True}]
    save_dataset(examples, path)
    loaded = load_dataset_from_disk(path)
    assert loaded == examples
