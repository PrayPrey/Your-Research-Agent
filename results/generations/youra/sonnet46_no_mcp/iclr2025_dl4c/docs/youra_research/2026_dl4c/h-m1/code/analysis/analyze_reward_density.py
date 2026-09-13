"""RewardDensityAnalyzer: Main orchestrator for H-M1 reward density analysis."""

import json
import os
import sys

# Allow running from any working directory
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from loader import (
    CONDITIONS,
    load_reward_density_logs,
    validate_full_training,
    compute_early_phase_density,
)
from stats import run_wilcoxon_test, check_assumption_a1, compute_phase_stats
from visualize import (
    plot_early_phase_bar,
    plot_timeseries,
    plot_wilcoxon_boxplot,
    plot_phase_comparison,
)

ANALYSIS_CONFIG = {
    "log_dir": "h-e1/logs",
    "figures_dir": "h-m1/figures",
    "results_dir": "h-m1/results",
    "results_file": "h-m1/results/wilcoxon_results.json",
    "significance_threshold": 0.05,
    "analysis_window_early": [0, 2500],
    "analysis_window_late": [2501, 5000],
    "conditions": CONDITIONS,
}

RESULTS_DIR = ANALYSIS_CONFIG["results_dir"]


def run_analysis(
    log_dir: str = ANALYSIS_CONFIG["log_dir"],
    figures_dir: str = ANALYSIS_CONFIG["figures_dir"],
) -> dict:
    """Main pipeline: load → validate → extract → test → visualize → report.
    Returns full results dict with gate_passed bool."""
    print("=" * 60)
    print("H-M1: Reward Density Mechanism Analysis")
    print("=" * 60)

    # 1. Load logs
    print("\n[1/6] Loading reward density logs...")
    logs = load_reward_density_logs(log_dir)
    print(f"  Loaded {len(logs)} condition CSVs")
    for cond, df in logs.items():
        print(f"    {cond}: {len(df)} rows")

    # 2. Validate
    print("\n[2/6] Validating training completeness...")
    all_valid, counts = validate_full_training(logs, min_rows=10)
    print(f"  All conditions valid: {all_valid} — counts: {counts}")

    # 3. Extract early-phase per condition
    print("\n[3/6] Extracting early-phase density arrays (steps 0-2500)...")
    early_vals = {}
    for cond in CONDITIONS:
        early_vals[cond] = compute_early_phase_density(logs[cond])
        print(f"    {cond}: {early_vals[cond]}")

    # 4. Wilcoxon test
    print("\n[4/6] Running Wilcoxon one-tailed test (curriculum > uniform)...")
    wilcoxon = run_wilcoxon_test(early_vals["curriculum"], early_vals["uniform"])
    print(f"  statistic={wilcoxon['statistic']:.4f}, p_value={wilcoxon['p_value']:.4f}")
    print(f"  curriculum_mean={wilcoxon['curriculum_mean']:.4f}, uniform_mean={wilcoxon['uniform_mean']:.4f}")
    print(f"  delta={wilcoxon['delta']:.4f}, passed={wilcoxon['passed']}")

    # 5. Check assumption A1 (easy_only >= curriculum)
    print("\n[5/6] Checking assumption A1 (easy_only >= curriculum)...")
    assumption_a1 = check_assumption_a1(early_vals["easy_only"], early_vals["curriculum"])
    print(f"  easy_only_mean={assumption_a1['easy_only_mean']:.4f}, "
          f"curriculum_mean={assumption_a1['curriculum_mean']:.4f}, "
          f"passed={assumption_a1['passed']}")

    # 6. Phase stats
    phase_stats = compute_phase_stats(logs)

    # 7. Generate figures
    print("\n[6/6] Generating figures...")
    os.makedirs(figures_dir, exist_ok=True)
    fig_bar = plot_early_phase_bar(phase_stats, figures_dir)
    fig_ts = plot_timeseries(logs, figures_dir)
    fig_box = plot_wilcoxon_boxplot(
        early_vals["curriculum"], early_vals["uniform"],
        wilcoxon["p_value"], figures_dir
    )
    fig_phase = plot_phase_comparison(phase_stats, figures_dir)
    figure_paths = [fig_bar, fig_ts, fig_box, fig_phase]
    print(f"  Generated {len(figure_paths)} figures")

    # 8. Gate evaluation
    gate_passed = bool(
        wilcoxon["p_value"] < ANALYSIS_CONFIG["significance_threshold"]
        and wilcoxon["curriculum_mean"] > wilcoxon["uniform_mean"]
    )

    results = {
        "gate_passed": gate_passed,
        "wilcoxon": wilcoxon,
        "assumption_a1": assumption_a1,
        "phase_stats": phase_stats,
        "figure_paths": figure_paths,
        "results_path": ANALYSIS_CONFIG["results_file"],
    }
    return results


def save_results(results: dict, results_dir: str = RESULTS_DIR) -> str:
    """Write results to {results_dir}/wilcoxon_results.json. Returns path."""
    os.makedirs(results_dir, exist_ok=True)
    out_path = os.path.join(results_dir, "wilcoxon_results.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {out_path}")
    return out_path


def print_summary(results: dict) -> None:
    """Print gate PASSED/FAILED, p_value, curriculum_mean, uniform_mean, delta."""
    w = results["wilcoxon"]
    gate = "PASSED ✓" if results["gate_passed"] else "FAILED ✗"
    print("\n" + "=" * 60)
    print(f"GATE RESULT: {gate}")
    print(f"  p_value       = {w['p_value']:.6f} (threshold: 0.05)")
    print(f"  curriculum    = {w['curriculum_mean']:.4f}")
    print(f"  uniform       = {w['uniform_mean']:.4f}")
    print(f"  delta         = {w['delta']:.4f}")
    a1 = results["assumption_a1"]
    print(f"  A1 check      = {'passed' if a1['passed'] else 'failed'} "
          f"(easy_only={a1['easy_only_mean']:.4f} vs curriculum={a1['curriculum_mean']:.4f})")
    print("=" * 60)


if __name__ == "__main__":
    results = run_analysis()
    save_results(results)
    print_summary(results)
    sys.exit(0 if results["gate_passed"] else 1)
