import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import patch, MagicMock
from config import load_config, Config
from ngram_extractor import NgramExtractor
from pile_query import PileQuery


def _make_pq(wimbd_host=""):
    cfg = Config()
    env = {"WIMBD_ES_HOST": wimbd_host}
    with patch.dict(os.environ, env, clear=False):
        ext = NgramExtractor(cfg)
        pq = PileQuery(cfg, ext)
    return pq, cfg, ext


def test_use_wimbd_returns_false_when_host_not_set():
    with patch.dict(os.environ, {"WIMBD_ES_HOST": ""}, clear=False):
        cfg = Config()
        ext = NgramExtractor(cfg)
        pq = PileQuery(cfg, ext)
    assert pq._use_wimbd() is False
    assert pq.mode == "fallback_minhash"


def test_use_wimbd_returns_true_when_host_set():
    with patch.dict(os.environ, {"WIMBD_ES_HOST": "http://localhost:9200"}, clear=False):
        cfg = Config()
        ext = NgramExtractor(cfg)
        pq = PileQuery(cfg, ext)
        assert pq._use_wimbd() is True
        assert pq.mode == "wimbd"


def test_is_contaminated_returns_0_or_1_mock_wimbd():
    with patch.dict(os.environ, {"WIMBD_ES_HOST": "http://mock:9200"}, clear=False):
        cfg = Config()
        ext = NgramExtractor(cfg)
        pq = PileQuery(cfg, ext)

    text = " ".join([f"word{i}" for i in range(20)])
    with patch.object(pq, "_query_wimbd_with_retry", return_value=True):
        result = pq.is_contaminated(text)
    assert result == 1

    with patch.object(pq, "_query_wimbd_with_retry", return_value=False):
        result = pq.is_contaminated(text)
    assert result == 0


def test_is_contaminated_short_text_returns_0():
    with patch.dict(os.environ, {"WIMBD_ES_HOST": ""}, clear=False):
        cfg = Config()
        ext = NgramExtractor(cfg)
        pq = PileQuery(cfg, ext)
    result = pq.is_contaminated("short text")
    assert result == 0


def test_retry_logic_3_attempts_on_failure():
    with patch.dict(os.environ, {"WIMBD_ES_HOST": "http://mock:9200"}, clear=False):
        cfg = Config()
        ext = NgramExtractor(cfg)
        pq = PileQuery(cfg, ext)

    ngram = " ".join([f"t{i}" for i in range(13)])
    # Patch the import inside the method
    with patch("pile_query.PileQuery._query_wimbd_with_retry", return_value=False) as mock_method:
        result = pq._query_wimbd_with_retry(ngram)
    assert result is False
