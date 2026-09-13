import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from c_score_calculator import CScoreCalculator
from config import CScoreConfig


def make_calc():
    return CScoreCalculator(CScoreConfig(n_bootstrap=100, seed=42))


def test_compute_c_score_basic():
    calc = make_calc()
    # Non-overlapping sets: high complementarity expected
    set_a = {"A", "B", "C"}
    set_b = {"D", "E", "F"}
    stratum = list("ABCDEFGHI")
    result = calc.compute_c_score(set_a, set_b, stratum)
    assert "c_score" in result
    assert "j_obs" in result
    assert "e_j" in result
    assert result["stratum_size"] == 9
    # J_obs = 0 (no overlap), E[J] > 0 => C_score = 1.0
    assert abs(result["j_obs"]) < 1e-9
    assert result["c_score"] == 1.0


def test_compute_c_score_full_overlap():
    calc = make_calc()
    # Full overlap: J_obs = E[J] => C_score ~ 0
    set_a = {"A", "B"}
    set_b = {"A", "B"}
    stratum = ["A", "B", "C", "D"]
    result = calc.compute_c_score(set_a, set_b, stratum)
    assert result["j_obs"] == 1.0
    assert result["c_score"] <= 0.0


def test_compute_c_score_empty_stratum():
    calc = make_calc()
    result = calc.compute_c_score({"A"}, {"B"}, [])
    assert result["stratum_size"] == 0
    assert result["c_score"] == 0.0


def test_bootstrap_c_score_ci_returns_keys():
    calc = make_calc()
    set_a = {"A", "B"}
    set_b = {"C", "D"}
    stratum = list("ABCDEFGHIJ")
    ci = calc.bootstrap_c_score_ci(set_a, set_b, stratum)
    assert "mean" in ci
    assert "ci_lower" in ci
    assert "ci_upper" in ci
    assert "p_value" in ci
    assert ci["n_bootstrap"] == 100


def test_define_eligibility_conditioned_stratum():
    calc = make_calc()
    fmd = {
        "HumanEval/0": ["syntax", "type"],
        "HumanEval/1": ["functional"],
        "HumanEval/2": ["type"],
        "HumanEval/3": ["syntax"],
    }
    mypy_eligible = {"HumanEval/0", "HumanEval/2"}
    stratum = calc.define_eligibility_conditioned_stratum(fmd, mypy_eligible)
    assert "HumanEval/0" in stratum
    assert "HumanEval/2" in stratum
    assert "HumanEval/1" not in stratum  # no "type" label
    assert "HumanEval/3" not in stratum  # not mypy_eligible


def test_define_stratum_uses_type_not_type_structural():
    calc = make_calc()
    fmd = {"HumanEval/0": ["type_structural"]}  # wrong label
    mypy_eligible = {"HumanEval/0"}
    stratum = calc.define_eligibility_conditioned_stratum(fmd, mypy_eligible)
    assert "HumanEval/0" not in stratum  # must use "type" not "type_structural"


def test_compute_difficulty_quintiles():
    calc = make_calc()
    problems = [f"P{i}" for i in range(10)]
    rates = {f"P{i}": i / 10 for i in range(10)}
    q = calc.compute_difficulty_quintiles(problems, rates)
    assert len(q) == 5
    total = sum(len(v) for v in q.values())
    assert total == 10


def test_compute_c_score_by_quintile():
    calc = make_calc()
    set_a = {"P0", "P1"}
    set_b = {"P5", "P6"}
    problems = [f"P{i}" for i in range(10)]
    rates = {f"P{i}": i / 10 for i in range(10)}
    quintiles = calc.compute_difficulty_quintiles(problems, rates)
    results = calc.compute_c_score_by_quintile(set_a, set_b, quintiles)
    assert len(results) == 5
    for r in results.values():
        assert "c_score" in r


def test_save_results(tmp_path):
    calc = make_calc()
    path = str(tmp_path / "c_score_results.json")
    calc.save_results(
        {"c_score": 0.5, "j_obs": 0.1, "e_j": 0.2, "r1": 0.3, "r2": 0.3,
         "intersection_size": 1, "union_size": 5, "stratum_size": 10},
        {"mean": 0.5, "ci_lower": 0.1, "ci_upper": 0.9, "p_value": 0.02, "n_bootstrap": 100},
        {"c_score": 0.4, "j_obs": 0.1, "e_j": 0.2, "r1": 0.2, "r2": 0.2,
         "intersection_size": 1, "union_size": 5, "stratum_size": 20},
        {0: {"c_score": 0.3}, 1: {"c_score": 0.5}},
        path,
    )
    import json
    data = json.load(open(path))
    assert "c_score" in data
    assert "quintile_results" in data
