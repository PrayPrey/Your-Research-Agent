"""Tests for data_pipeline.py spec compliance."""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_pipeline import download_halueval


def make_fake_cache(tmp_dir, n=20):
    """Create a fake HaluEval cache file."""
    data = [
        {"question": f"Q{i}?", "right_answer": f"correct{i}", "hallucinated_answer": f"wrong{i}"}
        for i in range(n)
    ]
    cache_path = os.path.join(tmp_dir, "qa_data.json")
    with open(cache_path, "w") as f:
        json.dump(data, f)
    return cache_path


def test_download_halueval_returns_list():
    with tempfile.TemporaryDirectory() as tmp:
        cache = make_fake_cache(tmp, n=20)
        save = os.path.join(tmp, "out.json")
        result = download_halueval(save_path=save, raw_cache=cache, n_questions=10, seed=42)
        assert isinstance(result, list), "Must return list"


def test_download_halueval_correct_count():
    with tempfile.TemporaryDirectory() as tmp:
        cache = make_fake_cache(tmp, n=30)
        save = os.path.join(tmp, "out.json")
        result = download_halueval(save_path=save, raw_cache=cache, n_questions=10, seed=42)
        assert len(result) == 10


def test_download_halueval_stratified():
    with tempfile.TemporaryDirectory() as tmp:
        cache = make_fake_cache(tmp, n=30)
        save = os.path.join(tmp, "out.json")
        result = download_halueval(save_path=save, raw_cache=cache, n_questions=10, seed=42)
        labels = [r["label"] for r in result]
        assert labels.count(0) == 5
        assert labels.count(1) == 5


def test_download_halueval_schema():
    with tempfile.TemporaryDirectory() as tmp:
        cache = make_fake_cache(tmp, n=20)
        save = os.path.join(tmp, "out.json")
        result = download_halueval(save_path=save, raw_cache=cache, n_questions=10, seed=42)
        for item in result:
            assert "question" in item
            assert "label" in item
            assert item["label"] in (0, 1)


def test_download_halueval_skips_if_exists():
    with tempfile.TemporaryDirectory() as tmp:
        preexist = [{"question": "pre", "label": 0}]
        save = os.path.join(tmp, "out.json")
        with open(save, "w") as f:
            json.dump(preexist, f)
        result = download_halueval(save_path=save, raw_cache="/nonexistent", n_questions=10)
        assert result == preexist, "Should return pre-existing file without re-downloading"
