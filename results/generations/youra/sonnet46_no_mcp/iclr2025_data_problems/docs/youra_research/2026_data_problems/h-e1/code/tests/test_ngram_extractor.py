import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import load_config, Config
from ngram_extractor import NgramExtractor


def test_extract_correct_13gram_count():
    cfg = load_config()
    ext = NgramExtractor(cfg)
    # 15 tokens -> 15-13+1 = 3 ngrams
    text = " ".join([f"word{i}" for i in range(15)])
    result = ext.extract(text)
    assert len(result) == 3


def test_extract_returns_empty_for_less_than_13_tokens():
    cfg = load_config()
    ext = NgramExtractor(cfg)
    text = "only twelve tokens here not enough to make thirteen gram ngrams ok"
    tokens = text.split()
    assert len(tokens) < 13 or True  # ensure we have a short text
    short_text = " ".join(["tok"] * 12)
    result = ext.extract(short_text)
    assert result == []


def test_extract_exactly_13_tokens_gives_1_ngram():
    cfg = load_config()
    ext = NgramExtractor(cfg)
    text = " ".join([f"w{i}" for i in range(13)])
    result = ext.extract(text)
    assert len(result) == 1
    assert result[0] == text


def test_extract_case_sensitivity_preserved():
    cfg = load_config()
    ext = NgramExtractor(cfg)
    text = " ".join(["Hello", "World"] + [f"word{i}" for i in range(11)])
    result = ext.extract(text)
    assert result[0].startswith("Hello World")


def test_extract_batch_skips_short_texts():
    cfg = load_config()
    ext = NgramExtractor(cfg)
    texts = [
        " ".join([f"w{i}" for i in range(15)]),  # long enough
        "short text",                              # too short
        " ".join([f"x{i}" for i in range(20)]),  # long enough
    ]
    results = ext.extract_batch(texts)
    assert len(results) == 3
    assert results[1] == []
    assert len(results[0]) > 0
    assert len(results[2]) > 0
