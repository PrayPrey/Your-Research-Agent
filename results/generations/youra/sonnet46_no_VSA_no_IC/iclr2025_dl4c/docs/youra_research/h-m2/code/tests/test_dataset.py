import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json, tempfile
import numpy as np
import pytest


def test_load_variance_50_ids_top_ids_key():
    from dataset import load_variance_50_ids
    data = {"top_ids": [10, 20, 30, 40, 50] * 10}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        path = f.name
    ids = load_variance_50_ids(path, k=5)
    assert ids == [10, 20, 30, 40, 50]
    os.unlink(path)


def test_load_variance_50_ids_fallback():
    """Falls back to sorting problems by variance_i if top_ids missing."""
    from dataset import load_variance_50_ids
    data = {
        "problems": {
            "1": {"variance_i": 0.1},
            "2": {"variance_i": 0.4},
            "3": {"variance_i": 0.25},
        }
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        path = f.name
    ids = load_variance_50_ids(path, k=2)
    assert ids[0] == 2  # highest variance_i
    os.unlink(path)


def test_load_random_50_ids_fixed_seed():
    from dataset import load_random_50_ids
    from datasets import Dataset

    ds = Dataset.from_dict({"task_id": list(range(100)), "text": ["x"] * 100,
                             "code": [""] * 100, "test_list": [[]] * 100})
    ids1 = load_random_50_ids(ds, k=50, seed=42)
    ids2 = load_random_50_ids(ds, k=50, seed=42)
    assert ids1 == ids2
    assert len(ids1) == 50


def test_load_random_50_ids_different_seeds():
    from dataset import load_random_50_ids
    from datasets import Dataset

    ds = Dataset.from_dict({"task_id": list(range(200)), "text": ["x"] * 200,
                             "code": [""] * 200, "test_list": [[]] * 200})
    ids1 = load_random_50_ids(ds, k=50, seed=42)
    ids2 = load_random_50_ids(ds, k=50, seed=99)
    assert ids1 != ids2
