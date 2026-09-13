import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
import pandas as pd
import pytest
from config import Config
from stats_analyzer import StatsAnalyzer

def make_wide(seed=42):
    rng = np.random.default_rng(seed)
    data = {
        "pile":      rng.uniform(0.0, 0.20, 59),
        "c4":        rng.uniform(0.0, 0.05, 59),
        "redpajama": rng.uniform(0.0, 0.10, 59),
    }
    return pd.DataFrame(data, index=[f"subtask_{i}" for i in range(59)])

def test_kruskal_wallis_returns_all_keys():
    cfg = Config()
    sa = StatsAnalyzer(cfg)
    wide = make_wide()
    result = sa.kruskal_wallis(wide)
    for key in ["kruskal_H", "kruskal_p", "gate_pass", "corpus_means", "max_pair_diff_pp"]:
        assert key in result

def test_kruskal_wallis_gate_pass_when_significant():
    cfg = Config()
    sa = StatsAnalyzer(cfg)
    wide = make_wide()  # distributions differ significantly
    result = sa.kruskal_wallis(wide)
    assert result["gate_pass"] == (result["kruskal_p"] < 0.05)

def test_dunn_posthoc_returns_3x3():
    cfg = Config()
    sa = StatsAnalyzer(cfg)
    wide = make_wide()
    dunn = sa.dunn_posthoc(wide)
    assert dunn.shape == (3, 3)
    assert list(dunn.columns) == ["pile", "c4", "redpajama"]

def test_assert_gate_raises_when_fails():
    cfg = Config()
    sa = StatsAnalyzer(cfg)
    with pytest.raises(AssertionError):
        sa.assert_gate(0.10)

def test_assert_gate_passes():
    cfg = Config()
    sa = StatsAnalyzer(cfg)
    sa.assert_gate(0.001)  # should not raise

def test_spearman_wimbd_returns_tuple():
    cfg = Config()
    sa = StatsAnalyzer(cfg)
    wide = make_wide()
    pile = wide["pile"]
    # Provide enough overlap with WIMBD_REFERENCE
    from stats_analyzer import WIMBD_REFERENCE
    # Patch pile index to match WIMBD keys
    pile_with_names = pd.Series(
        {k: v for k, v in zip(list(WIMBD_REFERENCE.keys())[:10], np.linspace(0.01, 0.17, 10))}
    )
    cfg.wimbd_spearman_min_rho = -1.0  # disable assertion for test
    rho, p = sa.spearman_wimbd(pile_with_names)
    assert isinstance(rho, float)
    assert isinstance(p, float)
