"""
Spec compliance tests for run_h_e1.py
Tests validate_data, analyze_thresholds, check_gate using synthetic DataFrames.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from run_h_e1 import validate_data, analyze_thresholds, check_gate


def _make_df(n_per_lang=50_000):
    """Synthetic 5-language DataFrame with realistic perplexity spread."""
    rng = np.random.default_rng(42)
    means = {"en": 50, "de": 120, "fr": 100, "es": 110, "it": 150}
    rows = []
    for lang, mu in means.items():
        ppl = rng.lognormal(mean=np.log(mu), sigma=0.8, size=n_per_lang)
        rows.append(pd.DataFrame({"language": lang, "ccnet_perplexity": ppl}))
    return pd.concat(rows, ignore_index=True)


# ─── validate_data ────────────────────────────────────────────────────────────

def test_validate_data_passes_good_df():
    df = _make_df(45_000)  # 225_000 rows total, 5 langs
    validate_data(df)  # should not raise


def test_validate_data_fails_too_few_rows():
    df = _make_df(30_000)  # 150_000 < 190_000
    with pytest.raises(ValueError, match="Too few rows"):
        validate_data(df)


def test_validate_data_fails_wrong_lang_count():
    df = _make_df(50_000)  # 250_000 total; drop 1 lang → 200_000 > 190_000
    df = df[df["language"] != "it"]
    with pytest.raises(ValueError, match="Expected 5 languages"):
        validate_data(df)


# ─── analyze_thresholds ───────────────────────────────────────────────────────

def test_analyze_thresholds_keys():
    df = _make_df(10_000)
    results = analyze_thresholds(df, k_values=[10, 30, 50])
    assert set(results.keys()) == {10, 30, 50}


def test_analyze_thresholds_cramers_v_range():
    df = _make_df(10_000)
    results = analyze_thresholds(df, k_values=[10, 30, 50])
    for k in [10, 30, 50]:
        v = results[k]["cramers_v"]
        assert 0.0 <= v <= 1.0, f"V={v} out of [0,1] at k={k}"


def test_analyze_thresholds_retention_rates_shape():
    df = _make_df(10_000)
    results = analyze_thresholds(df, k_values=[20])
    rr = results[20]["retention_rates"]
    assert set(rr.keys()) == {"de", "en", "es", "fr", "it"}


def test_analyze_thresholds_holm_key():
    df = _make_df(10_000)
    results = analyze_thresholds(df, k_values=[10, 20])
    for k in [10, 20]:
        assert "p_holm" in results[k]
        assert 0.0 <= results[k]["p_holm"] <= 1.0


# ─── check_gate ───────────────────────────────────────────────────────────────

def test_check_gate_returns_dict():
    df = _make_df(45_000)
    results = analyze_thresholds(df, k_values=[10, 20, 30, 40, 50])
    gate = check_gate(df, results)
    assert "gate_passed" in gate
    assert "indicators" in gate
    assert isinstance(gate["gate_passed"], bool)


def test_check_gate_indicators_keys():
    df = _make_df(45_000)
    results = analyze_thresholds(df, k_values=[10, 20, 30, 40, 50])
    gate = check_gate(df, results)
    expected_keys = {"data_loaded", "five_languages", "no_nan_perplexity",
                     "cramers_v_in_range", "holm_p_significant"}
    assert expected_keys.issubset(set(gate["indicators"].keys()))
