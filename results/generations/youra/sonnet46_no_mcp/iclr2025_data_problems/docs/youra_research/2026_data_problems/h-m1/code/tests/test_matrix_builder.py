import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pandas as pd
import pytest
from config import Config
from ngram_extractor import NgramExtractor
from matrix_builder import MatrixBuilder
from datasketch import MinHashLSH

def make_mock_lsh():
    return MinHashLSH(threshold=0.5, num_perm=128)

def test_query_cell_returns_dict():
    cfg = Config()
    ext = NgramExtractor(cfg)
    mb = MatrixBuilder(cfg, ext)
    lsh = make_mock_lsh()
    texts = [" ".join(["word"] * 20)] * 5
    result = mb.query_cell("test_subtask", texts, "pile", lsh)
    assert set(result.keys()) == {"subtask", "corpus", "n_items", "n_contaminated", "rate"}
    assert result["n_items"] == 5
    assert 0.0 <= result["rate"] <= 1.0

def test_to_wide_has_3_columns():
    cfg = Config()
    ext = NgramExtractor(cfg)
    mb = MatrixBuilder(cfg, ext)
    # Build minimal mock long df
    rows = []
    for st in [f"s{i}" for i in range(59)]:
        for corp in ["pile", "c4", "redpajama"]:
            rows.append({"subtask": st, "corpus": corp, "n_items": 10, "n_contaminated": 1, "rate": 0.1})
    df = pd.DataFrame(rows)
    wide = mb.to_wide(df)
    assert list(wide.columns) == ["pile", "c4", "redpajama"]
    assert len(wide) == 59
