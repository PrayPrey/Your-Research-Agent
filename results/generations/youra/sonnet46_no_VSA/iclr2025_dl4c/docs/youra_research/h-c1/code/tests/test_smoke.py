"""Smoke tests for H-C1 modules."""
import sys
import json
import tempfile
from pathlib import Path

# Add parent to path so imports work
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_config_imports():
    from config import CONDITIONS, SEEDS, MODEL_ID, BENCHMARKS, H_E2_DATASETS_DIR
    assert set(CONDITIONS) == {"humaneval_only", "mbpp_only", "leetcode_only", "equal_mix"}
    assert SEEDS == [42, 123, 777]
    assert "7b" in MODEL_ID.lower() or "7B" in MODEL_ID
    assert BENCHMARKS == ["humaneval", "mbpp"]
    print(f"[OK] config: MODEL_ID={MODEL_ID}")


def test_data_loader_files_exist():
    from config import H_E2_DATASETS_DIR, CONDITIONS
    for condition in CONDITIONS:
        p = Path(H_E2_DATASETS_DIR) / condition
        assert p.exists(), f"H-E2 dataset missing: {p}"
        print(f"[OK] data exists: {condition}")


def test_train_imports():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "train", str(Path(__file__).parent.parent / "train.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert hasattr(mod, "run_sft")
    assert hasattr(mod, "set_all_seeds")
    print("[OK] train.py imports and has run_sft")


def test_evaluate_imports():
    from evaluate import parse_evalplus_output
    # Test parsing from stdout fallback
    stdout = "Results: pass@1: 0.512, pass@5: 0.678"
    # Should not crash; returns float or -1
    result = parse_evalplus_output("/nonexistent.json", stdout)
    assert isinstance(result, float)
    print(f"[OK] evaluate.parse_evalplus_output: {result}")


def test_evalplus_importable():
    from evalplus.data import get_human_eval_plus
    n = len(get_human_eval_plus())
    assert n > 0
    print(f"[OK] evalplus: {n} HumanEval+ problems")


def test_analyze_eta_squared():
    from analyze import compute_eta_squared, compare_scales
    # 4 conditions, 3 seeds each
    vals = {
        "humaneval_only": [0.50, 0.52, 0.51],
        "mbpp_only": [0.38, 0.37, 0.39],
        "leetcode_only": [0.10, 0.09, 0.11],
        "equal_mix": [0.30, 0.28, 0.32],
    }
    eta = compute_eta_squared(vals)
    assert 0.0 <= eta <= 1.0
    print(f"[OK] compute_eta_squared: η²={eta:.4f}")

    # Test compare_scales: attenuation case
    eta_7b = {"humaneval": 0.35, "mbpp": 0.40}
    eta_1b = {"humaneval": 0.81, "mbpp": 0.75}
    gate = compare_scales(eta_7b, eta_1b)
    assert gate["gate_verdict"] == "PASS"
    assert gate["gate_satisfied"] is True
    print(f"[OK] compare_scales: PASS when η²_7B < η²_1.3B")

    # Null result case
    eta_7b_null = {"humaneval": 0.85, "mbpp": 0.80}
    gate_null = compare_scales(eta_7b_null, eta_1b)
    assert gate_null["gate_verdict"] == "NULL"
    print(f"[OK] compare_scales: NULL when no attenuation")


def test_analyze_verify_mechanism():
    from analyze import verify_h_c1_mechanism
    results_7b = {c: {"humaneval": [0.5, 0.51, 0.49], "mbpp": [0.38, 0.37, 0.39]}
                  for c in ["humaneval_only", "mbpp_only", "leetcode_only", "equal_mix"]}
    results_1b = {c: {"humaneval": [0.3, 0.28, 0.31], "mbpp": [0.25, 0.24, 0.26]}
                  for c in ["humaneval_only", "mbpp_only", "leetcode_only", "equal_mix"]}
    complete, indicators = verify_h_c1_mechanism(results_7b, results_1b)
    assert isinstance(complete, bool)
    assert "humaneval_complete" in indicators
    print(f"[OK] verify_h_c1_mechanism: complete={complete}")


def test_figures_render():
    from figures import plot_eta_sq_comparison
    eta_7b = {"humaneval": 0.35, "mbpp": 0.40}
    eta_1b = {"humaneval": 0.81, "mbpp": 0.75}
    plot_eta_sq_comparison(eta_7b, eta_1b, "/tmp/test_h_c1_eta_sq.png")
    assert Path("/tmp/test_h_c1_eta_sq.png").exists()
    print("[OK] figures.plot_eta_sq_comparison: rendered to /tmp")


def test_analyze_load_h_e2_results():
    from analyze import load_h_e2_results
    from config import H_E2_RESULTS_CSV
    results = load_h_e2_results(H_E2_RESULTS_CSV)
    assert isinstance(results, dict)
    # Should have at least some conditions
    assert len(results) > 0
    print(f"[OK] load_h_e2_results: {len(results)} conditions loaded")


if __name__ == "__main__":
    tests = [
        test_config_imports,
        test_data_loader_files_exist,
        test_train_imports,
        test_evaluate_imports,
        test_evalplus_importable,
        test_analyze_eta_squared,
        test_analyze_verify_mechanism,
        test_figures_render,
        test_analyze_load_h_e2_results,
    ]

    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"[FAIL] {t.__name__}: {e}")
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
