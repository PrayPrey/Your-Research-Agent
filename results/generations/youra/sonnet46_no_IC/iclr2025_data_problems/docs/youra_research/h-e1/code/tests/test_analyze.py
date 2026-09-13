"""Tests for analyze.py spec compliance."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd


def _make_df(direction_pass=True, p_low=True):
    """Synthetic results DataFrame with known properties."""
    np.random.seed(42)
    rows = []
    scales = [70, 160]
    ppls = [20, 35, 50]
    dedup_js = [0.7, 0.9]
    seeds = [1, 2, 3]
    for scale in scales:
        for ppl in ppls:
            for j in dedup_js:
                for seed in seeds:
                    # 70M peaks at lower PPL, 160M peaks at higher PPL
                    if direction_pass:
                        base_70 = 0.25 + (50 - ppl) * 0.001
                        base_160 = 0.27 + ppl * 0.001
                    else:
                        base_70 = 0.25
                        base_160 = 0.27
                    noise = np.random.normal(0, 0.002)
                    mmlu = (base_70 if scale == 70 else base_160) + noise
                    rows.append({
                        "scale": scale,
                        "ppl_threshold": ppl,
                        "dedup_j": j,
                        "corpus": "dolma",
                        "seed": seed,
                        "checkpoint_step": 25000,
                        "mmlu_4shot": max(0, mmlu),
                        "hellaswag_0shot": max(0, mmlu + 0.1),
                        "contamination_rate": 0.01,
                    })
    return pd.DataFrame(rows)


def test_load_results(tmp_path):
    from analyze import load_results
    df = _make_df()
    csv_path = str(tmp_path / "results.csv")
    df.to_csv(csv_path, index=False)
    loaded = load_results(csv_path)
    assert len(loaded) == len(df)
    assert "mmlu_4shot" in loaded.columns


def test_run_ancova_interaction():
    from analyze import run_ancova_interaction
    df = _make_df()
    result = run_ancova_interaction(df)
    assert "interaction_p" in result
    assert "interaction_eta2" in result
    assert 0.0 <= result["interaction_p"] <= 1.0
    assert result["interaction_eta2"] >= 0.0


def test_check_direction_pass():
    from analyze import check_direction
    df = _make_df(direction_pass=True)
    result = check_direction(df)
    assert "tau_star_70m" in result
    assert "tau_star_160m" in result
    assert "direction_confirmed" in result


def test_check_direction_fail():
    from analyze import check_direction
    df = _make_df(direction_pass=False)
    result = check_direction(df)
    # With flat data, direction may or may not confirm — just check structure
    assert isinstance(result["direction_confirmed"], bool)


def test_gate_check_pass():
    from analyze import gate_check
    result = gate_check({
        "interaction_p": 0.01,
        "interaction_eta2": 0.20,
        "direction_confirmed": True,
        "tau_star_70m": 20,
        "tau_star_160m": 50,
    })
    assert result["passed"] is True
    assert "PASS" in result["reason"]


def test_gate_check_fail_p():
    from analyze import gate_check
    result = gate_check({
        "interaction_p": 0.10,
        "interaction_eta2": 0.20,
        "direction_confirmed": True,
    })
    assert result["passed"] is False


def test_gate_check_fail_eta2():
    from analyze import gate_check
    result = gate_check({
        "interaction_p": 0.01,
        "interaction_eta2": 0.05,
        "direction_confirmed": True,
    })
    assert result["passed"] is False


def test_gate_check_fail_direction():
    from analyze import gate_check
    result = gate_check({
        "interaction_p": 0.01,
        "interaction_eta2": 0.20,
        "direction_confirmed": False,
    })
    assert result["passed"] is False


def test_compute_partial_eta2():
    from analyze import run_ancova_interaction, compute_partial_eta2
    df = _make_df()
    result = run_ancova_interaction(df)
    if result["anova_table"] is not None:
        eta2 = compute_partial_eta2(result["anova_table"], "C(scale):C(ppl_threshold)")
        assert 0.0 <= eta2 <= 1.0


def test_run_secondary_analyses():
    from analyze import run_secondary_analyses
    df = _make_df()
    result = run_secondary_analyses(df)
    assert isinstance(result, dict)
