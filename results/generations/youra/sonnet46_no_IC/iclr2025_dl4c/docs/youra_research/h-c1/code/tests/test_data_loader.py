"""Tests for data_loader.py."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data_loader import quality_filter, reservoir_sample


def test_quality_filter_pass():
    src = "x = 1\n" * 10
    assert quality_filter({"content": src}) is True


def test_quality_filter_avg_line_len():
    long_line = "a" * 101
    assert quality_filter({"content": long_line}) is False


def test_quality_filter_max_line_len():
    long_line = "a" * 1001
    assert quality_filter({"content": long_line + "\n" + "x = 1"}) is False


def test_quality_filter_alphanum():
    # mostly non-alphanum
    src = "!@#$%^&*()" * 100 + "a"
    assert quality_filter({"content": src}) is False


def test_quality_filter_empty():
    assert quality_filter({"content": ""}) is False


def test_reservoir_sample_count():
    items = [{"content": "x = 1\n" * 5} for _ in range(200)]
    result = reservoir_sample(iter(items), n=10)
    assert len(result) == 10


def test_reservoir_sample_quality_gate():
    # Mix: half fail quality (empty content), half pass
    items = [{"content": ""} if i % 2 == 0 else {"content": "x = 1\n" * 5} for i in range(200)]
    result = reservoir_sample(iter(items), n=5)
    assert len(result) == 5
    for r in result:
        assert r["content"] != ""
