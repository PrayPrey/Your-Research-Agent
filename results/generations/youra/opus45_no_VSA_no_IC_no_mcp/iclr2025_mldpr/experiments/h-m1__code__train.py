"""Main pipeline for h-m1: DNSI-gap correlation analysis."""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import CONFIG, GAP_DATA
from data import load_dnsi_from_h_e1, build_dataset
from metrics import CorrelationAnalyzer
from evaluate import check_gate, summarize

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def generate_figures(analysis: dict, names: list, dnsi: np.ndarray, gap: np.ndarray, out_dir: str) -> None:
    """Generate required visualizations."""
    os.makedirs(out_dir, exist_ok=True)

    # 1. Scatter + regression line + CI shading (MANDATORY)
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(dnsi, gap, s=100, c="blue", alpha=0.7, zorder=5)
    for i, name in enumerate(names):
        ax.annotate(name, (dnsi[i], gap[i]), fontsize=9, xytext=(5, 5), textcoords="offset points")

    # Regression line
    if len(dnsi) >= 2:
        z = np.polyfit(dnsi, gap, 1)
        p = np.poly1d(z)
        x_line = np.linspace(dnsi.min() - 0.1, dnsi.max() + 0.1, 100)
        ax.plot(x_line, p(x_line), "r--", label=f"Linear fit (R={analysis['r_pearson']:.3f})")

    ax.set_xlabel("DNSI")
    ax.set_ylabel("Generalization Gap")
    ax.set_title(f"DNSI vs Generalization Gap (n={len(names)})")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "scatter_regression.png"), dpi=150)
    plt.close()

    # 2. Bootstrap histogram
    boot_r = analysis.get("bootstrap_r", np.array([]))
    if len(boot_r) > 0:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.hist(boot_r, bins=50, edgecolor="black", alpha=0.7)
        ax.axvline(analysis["r_pearson"], color="red", linestyle="--", label=f"Observed R={analysis['r_pearson']:.3f}")
        ax.axvline(analysis["ci_95_lower"], color="orange", linestyle=":", label=f"95% CI: [{analysis['ci_95_lower']:.3f}, {analysis['ci_95_upper']:.3f}]")
        ax.axvline(analysis["ci_95_upper"], color="orange", linestyle=":")
        ax.set_xlabel("Pearson R")
        ax.set_ylabel("Count")
        ax.set_title("Bootstrap Distribution of Correlation Coefficient")
        ax.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, "bootstrap_histogram.png"), dpi=150)
        plt.close()

    # 3. Grouped bar (DNSI vs gap per benchmark)
    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(names))
    width = 0.35
    ax.bar(x - width/2, dnsi, width, label="DNSI")
    ax.bar(x + width/2, gap, width, label="Gen. Gap")
    ax.set_xlabel("Benchmark")
    ax.set_ylabel("Value")
    ax.set_title("DNSI and Generalization Gap by Benchmark")
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=45, ha="right")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "benchmark_comparison.png"), dpi=150)
    plt.close()

    # 4. Residual plot
    if len(dnsi) >= 2:
        z = np.polyfit(dnsi, gap, 1)
        p = np.poly1d(z)
        residuals = gap - p(dnsi)
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.scatter(dnsi, residuals, s=100, c="green", alpha=0.7)
        ax.axhline(0, color="black", linestyle="--")
        for i, name in enumerate(names):
            ax.annotate(name, (dnsi[i], residuals[i]), fontsize=9, xytext=(5, 5), textcoords="offset points")
        ax.set_xlabel("DNSI")
        ax.set_ylabel("Residual")
        ax.set_title("Residuals from Linear Fit")
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, "residual_plot.png"), dpi=150)
        plt.close()

    print(f"[FIGURES] Saved to {out_dir}")


def run_pipeline() -> dict:
    """Main correlation analysis pipeline."""
    print("=" * 60)
    print("[PIPELINE] Starting DNSI-Gap Correlation Analysis (h-m1)")
    print("=" * 60)

    # Load DNSI from h-e1
    print("\n[STEP 1] Loading DNSI from h-e1...")
    dnsi_dict = load_dnsi_from_h_e1()
    print(f"[DATA] DNSI keys from h-e1: {list(dnsi_dict.keys())}")
    print(f"[DATA] GAP_DATA keys: {list(GAP_DATA.keys())}")

    # Build dataset (intersection)
    print("\n[STEP 2] Building aligned dataset...")
    try:
        names, dnsi_arr, gap_arr = build_dataset(dnsi_dict, GAP_DATA)
        print(f"[DATA] Found {len(names)} overlapping benchmarks: {names}")
    except ValueError as e:
        print(f"[PIPELINE] FAILED: {e}")
        return {"success": False, "error": str(e)}

    # Run correlation analysis
    print("\n[STEP 3] Running correlation analysis...")
    analyzer = CorrelationAnalyzer()
    analysis = analyzer.analyze(dnsi_arr, gap_arr)

    print(f"\n[CORR] n = {analysis['n']}")
    print(f"[CORR] Pearson R = {analysis['r_pearson']:.4f} (p = {analysis['p_pearson']:.4f})")
    print(f"[CORR] Spearman ρ = {analysis['r_spearman']:.4f} (p = {analysis['p_spearman']:.4f})")
    print(f"[CORR] 95% CI: [{analysis['ci_95_lower']:.4f}, {analysis['ci_95_upper']:.4f}]")

    # Generate summary and check gate
    print("\n[STEP 4] Evaluating gate...")
    summary = summarize(analysis, names, dnsi_arr, gap_arr)
    gate_passed = summary["gate_passed"]

    # Generate figures
    print("\n[STEP 5] Generating figures...")
    figures_dir = os.path.join(os.path.dirname(__file__), "..", "figures")
    generate_figures(analysis, names, dnsi_arr, gap_arr, figures_dir)

    # Save results
    results_dir = os.path.join(os.path.dirname(__file__), CONFIG["results_dir"])
    os.makedirs(results_dir, exist_ok=True)
    results_path = os.path.join(results_dir, "correlation_results.json")

    results = {
        "success": True,
        "analysis": {k: v for k, v in analysis.items() if k != "bootstrap_r"},
        "summary": summary,
        "gate_passed": gate_passed,
    }

    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[RESULTS] Saved to {results_path}")

    # Final status
    print("\n" + "=" * 60)
    if analysis["hypothesis_supported"]:
        print(f"[CORR] SUCCESS: R = {analysis['r_pearson']:.3f} < -0.4, negative correlation confirmed")
    else:
        print(f"[CORR] FAILED: R = {analysis['r_pearson']:.3f}, threshold not met")

    if gate_passed:
        print("[GATE] MUST_WORK: PASSED")
    else:
        print("[GATE] MUST_WORK: FAILED")
        print(f"  R = {analysis['r_pearson']:.3f} > {CONFIG['fail_r_threshold']} or not negative")
    print("=" * 60)

    return results


if __name__ == "__main__":
    results = run_pipeline()
    print("\nEXPERIMENT COMPLETE")
