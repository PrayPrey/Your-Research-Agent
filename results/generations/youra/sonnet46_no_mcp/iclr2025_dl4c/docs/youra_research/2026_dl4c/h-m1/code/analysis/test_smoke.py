"""Integration smoke test for H-M1 analysis pipeline using synthetic CSV data."""

import json
import os
import sys
import tempfile
import numpy as np
import pandas as pd

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from loader import (
    load_reward_density_logs,
    validate_full_training,
    compute_early_phase_density,
    compute_late_phase_density,
)
from stats import run_wilcoxon_test, check_assumption_a1, compute_phase_stats
from visualize import (
    plot_early_phase_bar,
    plot_timeseries,
    plot_wilcoxon_boxplot,
    plot_phase_comparison,
)

CONDITIONS = ["curriculum", "uniform", "easy_only", "hard_only"]


def make_synthetic_csvs(tmpdir: str, n_rows: int = 10) -> None:
    """Create synthetic reward_density CSVs with known values for gate testing."""
    # curriculum higher density (0.8), uniform lower (0.5) → gate should PASS
    density_map = {
        "curriculum": 0.80,
        "uniform":    0.50,
        "easy_only":  0.85,
        "hard_only":  0.30,
    }
    os.makedirs(tmpdir, exist_ok=True)
    for cond in CONDITIONS:
        base = density_map[cond]
        rows = []
        for i in range(n_rows):
            step = i + 1
            density = min(1.0, max(0.0, base + np.random.normal(0, 0.02)))
            rows.append({"step": step, "reward_density": density})
        df = pd.DataFrame(rows)
        df.to_csv(os.path.join(tmpdir, f"reward_density_{cond}.csv"), index=False)


def test_loader(tmpdir: str, figures_dir: str) -> None:
    print("[TEST] loader.py ...")
    logs = load_reward_density_logs(tmpdir)
    assert set(logs.keys()) == set(CONDITIONS), "Missing conditions"
    for cond, df in logs.items():
        assert "step" in df.columns and "reward_density" in df.columns
        assert len(df) == 10

    all_valid, counts = validate_full_training(logs, min_rows=10)
    assert all_valid, f"validate_full_training failed: {counts}"

    early = compute_early_phase_density(logs["curriculum"], max_step=10, window_size=2)
    assert early.shape[0] == 5, f"Expected shape (5,), got {early.shape}"

    late = compute_late_phase_density(logs["curriculum"], min_step=5, window_size=1)
    assert late.ndim == 1
    print("  loader.py: OK")


def test_stats(tmpdir: str) -> dict:
    print("[TEST] stats.py ...")
    logs = load_reward_density_logs(tmpdir)

    # Use full-length early vals (n=5 for Wilcoxon, need at least 6 identical values)
    # Use synthetic arrays directly
    curriculum_vals = np.array([0.80, 0.81, 0.79, 0.82, 0.80])
    uniform_vals    = np.array([0.50, 0.51, 0.49, 0.52, 0.50])
    easy_only_vals  = np.array([0.85, 0.86, 0.84, 0.87, 0.85])

    w = run_wilcoxon_test(curriculum_vals, uniform_vals)
    assert "statistic" in w and "p_value" in w
    assert w["passed"] == (w["p_value"] < 0.05)
    assert w["curriculum_mean"] > w["uniform_mean"], "curriculum should be higher"
    print(f"  Wilcoxon p={w['p_value']:.4f}, passed={w['passed']}")

    a1 = check_assumption_a1(easy_only_vals, curriculum_vals)
    assert "passed" in a1
    print(f"  A1 check passed={a1['passed']}")

    # Build 5-row logs for compute_phase_stats
    mini_logs = {}
    for cond in CONDITIONS:
        mini_logs[cond] = pd.DataFrame({
            "step": list(range(1, 11)),
            "reward_density": [0.7] * 10
        })
    ps = compute_phase_stats(mini_logs)
    for cond in CONDITIONS:
        assert "early" in ps[cond] and "late" in ps[cond]
    print("  stats.py: OK")
    return w


def test_visualizer(tmpdir: str, figures_dir: str, p_value: float) -> None:
    print("[TEST] visualize.py ...")
    os.makedirs(figures_dir, exist_ok=True)

    mini_logs = {}
    for cond in CONDITIONS:
        mini_logs[cond] = pd.DataFrame({
            "step": list(range(1, 11)),
            "reward_density": [0.7 if cond == "curriculum" else 0.5] * 10
        })
    mini_phase_stats = compute_phase_stats(mini_logs)

    p1 = plot_early_phase_bar(mini_phase_stats, figures_dir)
    assert os.path.exists(p1), f"Missing: {p1}"

    p2 = plot_timeseries(mini_logs, figures_dir)
    assert os.path.exists(p2), f"Missing: {p2}"

    c_vals = np.array([0.80, 0.81, 0.79, 0.82, 0.80])
    u_vals = np.array([0.50, 0.51, 0.49, 0.52, 0.50])
    p3 = plot_wilcoxon_boxplot(c_vals, u_vals, p_value, figures_dir)
    assert os.path.exists(p3), f"Missing: {p3}"

    p4 = plot_phase_comparison(mini_phase_stats, figures_dir)
    assert os.path.exists(p4), f"Missing: {p4}"

    print(f"  4 figures generated in {figures_dir}")
    print("  visualize.py: OK")


def test_gate_logic() -> None:
    print("[TEST] gate logic ...")
    # PASS case
    curriculum_vals = np.array([0.80, 0.81, 0.79, 0.82, 0.80])
    uniform_vals    = np.array([0.50, 0.51, 0.49, 0.52, 0.50])
    w = run_wilcoxon_test(curriculum_vals, uniform_vals)
    gate_passed = (w["p_value"] < 0.05) and (w["curriculum_mean"] > w["uniform_mean"])
    print(f"  PASS case: gate_passed={gate_passed}, p={w['p_value']:.4f}")

    # FAIL case (equal values)
    eq_vals = np.array([0.60, 0.60, 0.60, 0.60, 0.60])
    try:
        w_fail = run_wilcoxon_test(eq_vals, eq_vals)
        gate_fail = (w_fail["p_value"] < 0.05) and (w_fail["curriculum_mean"] > w_fail["uniform_mean"])
        print(f"  FAIL case: gate_passed={gate_fail}")
    except Exception as e:
        print(f"  FAIL case raised (expected for zero diff): {type(e).__name__}")
    print("  gate logic: OK")


def test_results_json(figures_dir: str, results_dir: str) -> None:
    print("[TEST] results JSON schema ...")
    os.makedirs(results_dir, exist_ok=True)

    curriculum_vals = np.array([0.80, 0.81, 0.79, 0.82, 0.80])
    uniform_vals    = np.array([0.50, 0.51, 0.49, 0.52, 0.50])
    easy_only_vals  = np.array([0.85, 0.86, 0.84, 0.87, 0.85])

    w = run_wilcoxon_test(curriculum_vals, uniform_vals)
    a1 = check_assumption_a1(easy_only_vals, curriculum_vals)
    gate_passed = (w["p_value"] < 0.05) and (w["curriculum_mean"] > w["uniform_mean"])

    results = {
        "gate_passed": gate_passed,
        "wilcoxon": w,
        "assumption_a1": a1,
        "phase_stats": {},
        "figure_paths": [],
        "results_path": os.path.join(results_dir, "wilcoxon_results.json"),
    }
    out_path = os.path.join(results_dir, "wilcoxon_results.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)

    with open(out_path) as f:
        loaded = json.load(f)
    assert "gate_passed" in loaded
    assert "wilcoxon" in loaded
    assert isinstance(loaded["gate_passed"], bool)
    print(f"  JSON valid, gate_passed={loaded['gate_passed']}")
    print("  results JSON: OK")


def main():
    print("=" * 60)
    print("H-M1 Integration Smoke Test")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        figures_dir = os.path.join(tmpdir, "figures")
        results_dir = os.path.join(tmpdir, "results")

        np.random.seed(42)
        make_synthetic_csvs(tmpdir, n_rows=10)

        test_loader(tmpdir, figures_dir)
        w = test_stats(tmpdir)
        test_visualizer(tmpdir, figures_dir, w["p_value"])
        test_gate_logic()
        test_results_json(figures_dir, results_dir)

    print("\n" + "=" * 60)
    print("ALL SMOKE TESTS PASSED ✓")
    print("=" * 60)


if __name__ == "__main__":
    main()
