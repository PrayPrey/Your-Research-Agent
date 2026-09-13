import pandas as pd
from src.verification.coexistence import verify_signal_coexistence


def _make_df(n, rm_const=False, gold_const=False):
    rows = []
    for i in range(n):
        rows.append({
            "kl_budget": float(i),
            "rm_score": 1.0 if rm_const else float(i) * 0.3,
            "gold_preference": 0.5 if gold_const else 0.5 + i * 0.02,
        })
    return pd.DataFrame(rows)


def test_pass_condition():
    df = _make_df(7)
    res = verify_signal_coexistence(df, "Test")
    assert res["passed"] is True
    assert res["gate_satisfied"] is True
    assert res["n_kl_levels"] == 7


def test_fail_too_few_rows():
    df = _make_df(4)
    res = verify_signal_coexistence(df, "Test")
    assert res["passed"] is False
    assert res["gate_satisfied"] is False


def test_fail_missing_column():
    df = pd.DataFrame({"kl_budget": [0, 1, 2, 3, 4], "rm_score": [1, 2, 3, 4, 5]})
    res = verify_signal_coexistence(df, "Test")
    assert res["passed"] is False
    assert "gold_preference" in res["reason"]


def test_empty_dataframe():
    df = pd.DataFrame({"kl_budget": [], "rm_score": [], "gold_preference": []})
    res = verify_signal_coexistence(df, "Test")
    assert res["n_kl_levels"] == 0
    assert res["passed"] is False


def test_zero_variation_rm():
    df = _make_df(7, rm_const=True)
    res = verify_signal_coexistence(df, "Test")
    assert res["passed"] is False
    assert res["rm_variation"] == 0.0


def test_exactly_5_rows():
    df = _make_df(5)
    res = verify_signal_coexistence(df, "Test")
    assert res["gate_satisfied"] is True
    assert res["n_kl_levels"] == 5
