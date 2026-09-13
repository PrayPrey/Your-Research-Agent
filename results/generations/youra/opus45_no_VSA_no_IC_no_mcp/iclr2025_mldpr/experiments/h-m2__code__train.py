"""Main pipeline: h-e1 bridge → temporal DNSI → regression → gate."""

import sys
import os

# Inject h-e1 code path FIRST to avoid config collision
H_E1_CODE_DIR = os.path.join(os.path.dirname(__file__), "../../h-e1/code")
sys.path.insert(0, H_E1_CODE_DIR)

# h-e1 imports (will use h-e1/code/config.py)
from data import load_data
from metrics import DNSIComputer

# Remove h-e1 from path to load h-m2 modules
sys.path.pop(0)

import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# h-m2 config
from m2_config import CUTOFF_DATE, N_BOOTSTRAP, SEED, FIGURES_DIR, GAP_GROUND_TRUTH
from temporal_dnsi import TemporalDNSIComputer
from analysis import TemporalPredictionAnalyzer
from evaluate import check_gate, summarize


def load_matched_benchmarks() -> dict:
    """Load h-e1 benchmark data."""
    # load_data() uses relative paths, so cd to h-e1/code
    original_cwd = os.getcwd()
    os.chdir(H_E1_CODE_DIR)
    try:
        matched = load_data()
    finally:
        os.chdir(original_cwd)
    if not matched:
        print("[BRIDGE] FAILED: h-e1 load_data() returned no benchmarks")
    else:
        print(f"[BRIDGE] Loaded {len(matched)} benchmarks from h-e1")
    return matched


def align_dnsi_gap(matched: dict, dnsi_computer: TemporalDNSIComputer) -> tuple:
    """Align pre-cutoff DNSI with post-cutoff gaps."""
    names, dnsi_vals, gap_vals = [], [], []
    for bench, meta in GAP_GROUND_TRUTH.items():
        source_bench = meta.get("uses_history_of", bench)
        if source_bench not in matched:
            print(f"[ALIGN] SKIP {bench}: source '{source_bench}' not matched")
            continue
        entry = matched[source_bench]
        dnsi = dnsi_computer.compute_dnsi_pre_cutoff(
            entry["history"], entry["difficulty_proxy"]
        )
        if dnsi is None:
            print(f"[ALIGN] SKIP {bench}: insufficient pre-cutoff DNSI data")
            continue
        names.append(bench)
        dnsi_vals.append(dnsi)
        gap_vals.append(meta["gap"])
        print(f"[ALIGN] {bench}: DNSI={dnsi:.4f}, gap={meta['gap']:.3f}")
    return names, dnsi_vals, gap_vals


def generate_figures(dnsi: np.ndarray, gap: np.ndarray, results: dict,
                     bootstrap_r2: np.ndarray, out_dir: str) -> None:
    """Generate visualization figures."""
    os.makedirs(out_dir, exist_ok=True)

    if len(dnsi) < 2:
        print("[FIGURES] SKIP: insufficient data")
        return

    # Scatter with regression line
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(dnsi, gap, s=100, c="blue", alpha=0.7, label="Benchmarks")
    x_line = np.linspace(dnsi.min(), dnsi.max(), 100)
    y_line = results["slope"] * x_line + results["intercept"]
    ax.plot(x_line, y_line, "r-", linewidth=2, label="Regression")
    ax.set_xlabel("Pre-2019 DNSI")
    ax.set_ylabel("Post-2019 Generalization Gap")
    ax.set_title(f"DNSI vs Gap (R²={results['r2']:.3f})")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "scatter_regression.png"), dpi=150)
    plt.close()

    # Bootstrap histogram
    if bootstrap_r2.size > 0:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.hist(bootstrap_r2, bins=50, alpha=0.7, color="steelblue")
        ax.axvline(results["ci_95_lower"], color="red", linestyle="--", label="95% CI")
        ax.axvline(results["ci_95_upper"], color="red", linestyle="--")
        ax.set_xlabel("Bootstrap R²")
        ax.set_ylabel("Frequency")
        ax.set_title("Bootstrap R² Distribution")
        ax.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, "bootstrap_hist.png"), dpi=150)
        plt.close()

    print(f"[FIGURES] Saved to {out_dir}/")


def run_pipeline() -> dict:
    """Full experiment pipeline."""
    print("[TEMPORAL] Starting h-m2 temporal prediction analysis")

    # Load h-e1 data
    matched = load_matched_benchmarks()
    if not matched:
        return {"gate_result": "FAIL", "error": "no_data"}

    # Setup temporal DNSI computer
    base_dnsi = DNSIComputer(window_months=6)
    dnsi_computer = TemporalDNSIComputer(base_dnsi, cutoff_date=CUTOFF_DATE)

    # Align DNSI with gaps
    names, dnsi_vals, gap_vals = align_dnsi_gap(matched, dnsi_computer)
    if len(names) < 2:
        print(f"[ALIGN] FAILED: <2 aligned benchmarks ({len(names)}), cannot regress")
        return {"gate_result": "FAIL", "error": "insufficient_alignment", "n": len(names)}

    print(f"[TEMPORAL] Analyzing {len(names)} benchmark predictions...")

    # Run analysis
    analyzer = TemporalPredictionAnalyzer(n_bootstrap=N_BOOTSTRAP, seed=SEED)
    dnsi_arr = np.array(dnsi_vals)
    gap_arr = np.array(gap_vals)
    results = analyzer.analyze(dnsi_arr, gap_arr)

    if "error" in results:
        print(f"[TEMPORAL] FAILED: {results['error']}")
        return {"gate_result": "FAIL", **results}

    # Gate evaluation
    gate = check_gate(results)
    results = {**results, **summarize(results), "gate_result": gate, "benchmarks": names}

    # Log result
    if gate == "PASS":
        print(f"[TEMPORAL] SUCCESS: R² = {results['r2']:.4f} > 0.3")
    elif gate == "FAIL":
        print(f"[TEMPORAL] FAILED: R² = {results['r2']:.4f} < 0.1")
    else:
        print(f"[TEMPORAL] MARGINAL: R² = {results['r2']:.4f} (0.1 <= R² <= 0.3)")

    # Generate figures
    bootstrap_r2 = analyzer._bootstrap_r2(dnsi_arr, gap_arr)
    generate_figures(dnsi_arr, gap_arr, results, bootstrap_r2, FIGURES_DIR)

    # Save results
    with open("results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"[TEMPORAL] Results saved to results.json")

    return results


if __name__ == "__main__":
    results = run_pipeline()
    print(f"\n[FINAL] Gate result: {results.get('gate_result', 'UNKNOWN')}")
    print("EXPERIMENT COMPLETE")
