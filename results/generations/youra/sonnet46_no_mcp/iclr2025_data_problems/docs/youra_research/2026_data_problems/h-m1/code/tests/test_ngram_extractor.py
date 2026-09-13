import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import Config
from ngram_extractor import NgramExtractor

def test_extract_short_text_returns_empty():
    cfg = Config()
    ext = NgramExtractor(cfg)
    assert ext.extract("short text") == []

def test_extract_correct_count():
    cfg = Config()
    ext = NgramExtractor(cfg)
    tokens = ["word"] * 20
    text = " ".join(tokens)
    grams = ext.extract(text)
    assert len(grams) == 20 - 13 + 1

def test_text_to_minhash_returns_minhash():
    from datasketch import MinHash
    cfg = Config()
    ext = NgramExtractor(cfg)
    text = " ".join(["word"] * 20)
    m = ext.text_to_minhash(text)
    assert isinstance(m, MinHash)
    assert m.num_perm == 128
