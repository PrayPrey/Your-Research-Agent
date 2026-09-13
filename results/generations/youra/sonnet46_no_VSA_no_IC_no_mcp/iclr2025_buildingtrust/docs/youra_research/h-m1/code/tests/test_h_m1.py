"""Integration tests for H-M1 modules."""
import sys
import os
import numpy as np
import pytest

# Add code dir to path
CODE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)


def test_config_imports():
    from config import (
        H_E1_CODE_PATH, H_E1_RESULTS_DIR, RESULTS_DIR, FIGURES_DIR,
        SEED, N_BINS, CLEAN_ECE_H_E1, DELTA_ECE_H_E1, PRESERVE_RATE_GATE,
        SPLITS, SPLIT_FILE_MAP
    )
    assert N_BINS == 15
    assert CLEAN_ECE_H_E1 == pytest.approx(0.279)
    assert PRESERVE_RATE_GATE == pytest.approx(0.80)
    assert "advglue_mnli" in SPLITS
    assert "mnli" in SPLITS


def test_stratifier_advglue():
    from stratifier import build_strata, compute_preservation_rate
    strata = build_strata("advglue_mnli", 100)
    assert "high_pres_all" in strata
    assert strata["high_pres_all"].sum() == 100
    rate = compute_preservation_rate(strata)
    assert rate == pytest.approx(1.0)


def test_stratifier_anli():
    from stratifier import build_strata, compute_preservation_rate
    strata = build_strata("anli_r3", 50)
    assert "anli_r3_high_pres" in strata
    assert compute_preservation_rate(strata) == pytest.approx(1.0)


def test_stratifier_mnli():
    from stratifier import build_strata
    strata = build_strata("mnli", 200)
    assert "clean_baseline" in strata


def test_gate_verifier_pass():
    from gate_verifier import verify_gate
    passed, indicators = verify_gate(
        preservation_rate=1.0,
        stratum_ece=0.350,
        clean_ece=0.279,
        h_e1_delta=0.071,
    )
    assert passed is True
    assert indicators["preservation_rate_ok"] is True
    assert indicators["delta_ece_positive"] is True


def test_gate_verifier_fail_low_pres():
    from gate_verifier import verify_gate
    passed, indicators = verify_gate(
        preservation_rate=0.5,
        stratum_ece=0.350,
        clean_ece=0.279,
    )
    assert passed is False
    assert indicators["preservation_rate_ok"] is False


def test_gate_verifier_fail_negative_delta():
    from gate_verifier import verify_gate
    passed, indicators = verify_gate(
        preservation_rate=1.0,
        stratum_ece=0.200,
        clean_ece=0.279,
    )
    assert passed is False
    assert indicators["delta_ece_positive"] is False


def test_ece_analyzer_compute_delta():
    from ece_analyzer import compute_delta_ece
    assert compute_delta_ece(0.350, 0.279) == pytest.approx(0.071, abs=1e-6)
    assert compute_delta_ece(0.200, 0.279) == pytest.approx(-0.079, abs=1e-6)


def test_ece_analyzer_check_anli_gradient():
    from ece_analyzer import check_anli_gradient
    # Gradient holds
    results = {
        "anli_r1": {"delta_ece": 0.010},
        "anli_r2": {"delta_ece": 0.020},
        "anli_r3": {"delta_ece": 0.025},
    }
    assert check_anli_gradient(results) is True
    # Gradient fails
    results["anli_r3"]["delta_ece"] = 0.005
    assert check_anli_gradient(results) is False


def test_ece_analyzer_empty_mask():
    from config import H_E1_CODE_PATH
    if H_E1_CODE_PATH not in sys.path:
        sys.path.insert(0, H_E1_CODE_PATH)
    from ece_analyzer import compute_stratum_ece
    cache = {"conf": np.array([0.8, 0.6], dtype=np.float32), "correct": np.array([1, 0])}
    mask = np.array([False, False])
    with pytest.raises(ValueError, match="Empty stratum"):
        compute_stratum_ece(cache, mask)


def test_ablations_bin_count():
    from config import H_E1_CODE_PATH
    if H_E1_CODE_PATH not in sys.path:
        sys.path.insert(0, H_E1_CODE_PATH)
    from ablations import ablation_bin_count
    np.random.seed(42)
    n = 200
    cache = {
        "conf": np.random.uniform(0.3, 0.9, n).astype(np.float32),
        "correct": (np.random.rand(n) > 0.4).astype(np.int32),
    }
    mask = np.ones(n, dtype=bool)
    result = ablation_bin_count(cache, mask, bin_counts=(10, 15, 20))
    assert set(result.keys()) == {10, 15, 20}
    for ece in result.values():
        assert 0.0 <= ece <= 1.0


def test_cache_loader_missing():
    from cache_loader import load_split_cache
    with pytest.raises(FileNotFoundError, match="Re-run H-E1"):
        load_split_cache("advglue_mnli", "/nonexistent/path", {"advglue_mnli": "missing.jsonl"})


def test_run_all_strata_with_synthetic():
    from config import H_E1_CODE_PATH, CLEAN_ECE_H_E1
    if H_E1_CODE_PATH not in sys.path:
        sys.path.insert(0, H_E1_CODE_PATH)
    from ece_analyzer import run_all_strata
    np.random.seed(1)
    n = 200
    caches = {
        "advglue_mnli": {
            "conf": np.random.uniform(0.4, 0.9, n).astype(np.float32),
            "correct": (np.random.rand(n) > 0.5).astype(np.int32),
        },
        "anli_r1": {
            "conf": np.random.uniform(0.4, 0.8, n).astype(np.float32),
            "correct": (np.random.rand(n) > 0.6).astype(np.int32),
        },
    }
    results = run_all_strata(caches, clean_ece=CLEAN_ECE_H_E1)
    assert "advglue_mnli" in results
    assert "anli_r1" in results
    for split, res in results.items():
        assert "ece" in res
        assert "delta_ece" in res
        assert "n" in res
        assert 0.0 <= res["ece"] <= 1.0
