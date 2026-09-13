#!/usr/bin/env python3
"""Main orchestrator for h-c1: Temporal Early-Run Robustness Check.

Tests: Does metadata-variance effect persist in first-50-runs subsample
(within 90 days of dataset upload), ruling out reverse causality?

Gate: SHOULD_WORK - pipeline continues with warnings if fails.
"""
import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# h-c1 config first (before adding h-e1 to path)
from config import (
    PATHS, RANDOM_SEED, N_BOOTSTRAP,
    FULL_SAMPLE_EFFECT_PCT, PERSISTENCE_RATIO_MIN, RELATIVE_REDUCTION_MIN,
    SUCCESS_CRITERIA, MIN_DATASETS_EARLY
)

# Add h-e1 code to path for reusing analysis functions
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../h-e1/code")))
from generate_synthetic_temporal import generate_temporal_runs
from filter_early import filter_early_runs, validate_sample_size
from h_c1_analysis import build_early_analysis_dataset, run_early_effect_analysis, compute_persistence_ratio


def plot_effect_comparison(early_effect: dict, output_dir: str):
    """Plot early-run vs full-sample effect comparison."""
    os.makedirs(output_dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 6))

    effects = [FULL_SAMPLE_EFFECT_PCT, early_effect["relative_reduction_pct"]]
    labels = ["Full Sample\n(h-e1: all runs)", "Early Subsample\n(h-c1: first 50 runs\n≤90 days)"]
    colors = ["#2ecc71", "#3498db"]

    bars = ax.bar(labels, effects, color=colors, edgecolor="black", linewidth=1.2)

    # Add CI error bar for early effect
    if early_effect["ci_lower"] is not None:
        ci_low = early_effect["ci_lower"] * 100
        ci_high = early_effect["ci_upper"] * 100
        ax.errorbar(1, early_effect["relative_reduction_pct"],
                    yerr=[[early_effect["relative_reduction_pct"] - ci_low],
                          [ci_high - early_effect["relative_reduction_pct"]]],
                    fmt="none", color="black", capsize=5, capthick=2)

    # Threshold line
    ax.axhline(y=20, color="red", linestyle="--", linewidth=2, label="Pass threshold (20%)")

    # Labels
    ax.set_ylabel("Relative IQR Reduction (%)", fontsize=12)
    ax.set_title("Temporal Robustness: Metadata Effect Persists in Early Runs", fontsize=14)
    ax.legend(loc="upper right")

    # Value labels on bars
    for bar, val in zip(bars, effects):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f"{val:.1f}%", ha="center", va="bottom", fontsize=11, fontweight="bold")

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "effect_comparison.png"), dpi=150)
    plt.close()
    print(f"  Saved effect_comparison.png")


def plot_temporal_decay(runs_df: pd.DataFrame, output_dir: str):
    """Plot effect size vs days-since-upload."""
    os.makedirs(output_dir, exist_ok=True)

    # Bin by days
    runs_df = runs_df.copy()
    runs_df["days_bin"] = pd.cut(runs_df["days_since_upload"] if "days_since_upload" in runs_df.columns
                                  else (pd.to_datetime(runs_df["upload_time"]) -
                                        pd.to_datetime(runs_df["upload_date"])).dt.days,
                                  bins=[0, 30, 60, 90, 180, 365],
                                  labels=["0-30", "31-60", "61-90", "91-180", "181-365"])

    fig, ax = plt.subplots(figsize=(10, 6))

    for meta_group, color, label in [("low", "#e74c3c", "Low metadata (Q1)"),
                                      ("high", "#27ae60", "High metadata (Q4)")]:
        q1 = runs_df["metadata_score"].quantile(0.25)
        q3 = runs_df["metadata_score"].quantile(0.75)

        if meta_group == "low":
            subset = runs_df[runs_df["metadata_score"] <= q1]
        else:
            subset = runs_df[runs_df["metadata_score"] >= q3]

        iqr_by_bin = subset.groupby("days_bin")["predictive_accuracy"].agg(
            lambda x: x.quantile(0.75) - x.quantile(0.25)
        )
        ax.plot(iqr_by_bin.index.astype(str), iqr_by_bin.values,
                marker="o", linewidth=2, markersize=8, color=color, label=label)

    ax.axvline(x=2.5, color="gray", linestyle=":", linewidth=2, label="90-day cutoff")
    ax.set_xlabel("Days Since Dataset Upload", fontsize=12)
    ax.set_ylabel("IQR of Predictive Accuracy", fontsize=12)
    ax.set_title("Temporal Decay: IQR by Time Period", fontsize=14)
    ax.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "temporal_decay.png"), dpi=150)
    plt.close()
    print(f"  Saved temporal_decay.png")


def main():
    print("=" * 60)
    print("h-c1: Temporal Early-Run Robustness Check")
    print("=" * 60)
    np.random.seed(RANDOM_SEED)

    # Step 1: Generate synthetic temporal data
    print("\n[1/6] Generating synthetic temporal data...")
    runs_df = generate_temporal_runs()

    # Step 2: Filter to early runs
    print("\n[2/6] Filtering to early runs (first 50, ≤90 days)...")
    early_runs = filter_early_runs(runs_df)
    print(f"  Full sample: {len(runs_df)} runs")
    print(f"  Early subsample: {len(early_runs)} runs")

    # Step 3: Validate sample size
    print("\n[3/6] Validating sample size...")
    sample_validation = validate_sample_size(early_runs)
    print(f"  Datasets with ≥5 early runs: {sample_validation['n_datasets']}")
    print(f"  Sample size pass: {sample_validation['pass']}")

    if not sample_validation["pass"]:
        print(f"  WARNING: Only {sample_validation['n_datasets']} datasets, need {MIN_DATASETS_EARLY}")

    # Step 4: Build analysis dataset
    print("\n[4/6] Building early analysis dataset...")
    early_analysis_df = build_early_analysis_dataset(early_runs)
    print(f"  Analysis groups: {len(early_analysis_df)}")

    # Step 5: Compute quartile effect + bootstrap CI
    print("\n[5/6] Computing quartile effect + bootstrap CI...")
    early_effect = run_early_effect_analysis(early_analysis_df, n_boot=N_BOOTSTRAP)
    print(f"  IQR (bottom quartile): {early_effect['iqr_bottom']:.4f}")
    print(f"  IQR (top quartile): {early_effect['iqr_top']:.4f}")
    print(f"  Relative IQR reduction: {early_effect['relative_reduction_pct']:.1f}%")
    print(f"  95% CI: [{early_effect['ci_lower']*100:.1f}%, {early_effect['ci_upper']*100:.1f}%]")

    # Step 6: Compute persistence ratio + gate decision
    print("\n[6/6] Computing persistence ratio + gate decision...")
    persistence_ratio = compute_persistence_ratio(early_effect["relative_reduction_pct"])
    print(f"  Full-sample effect (h-e1): {FULL_SAMPLE_EFFECT_PCT:.1f}%")
    print(f"  Early-run effect (h-c1): {early_effect['relative_reduction_pct']:.1f}%")
    print(f"  Persistence ratio: {persistence_ratio:.2f}")

    # Gate decision
    passes_reduction = early_effect["relative_reduction_pct"] >= RELATIVE_REDUCTION_MIN * 100
    passes_persistence = persistence_ratio >= PERSISTENCE_RATIO_MIN
    gate_pass = passes_reduction and passes_persistence

    print("\n" + "=" * 60)
    print("GATE DECISION (SHOULD_WORK)")
    print("=" * 60)
    print(f"  ✓ Relative IQR reduction ≥20%: {passes_reduction} ({early_effect['relative_reduction_pct']:.1f}%)")
    print(f"  ✓ Persistence ratio ≥50%: {passes_persistence} ({persistence_ratio:.2f})")
    print(f"  RESULT: {'PASS' if gate_pass else 'FAIL'}")
    print("=" * 60)

    # Save results
    os.makedirs("results", exist_ok=True)
    results = {
        "hypothesis": "h-c1",
        "gate_type": "SHOULD_WORK",
        "gate_pass": bool(gate_pass),
        "early_effect": {
            "iqr_top": float(early_effect["iqr_top"]),
            "iqr_bottom": float(early_effect["iqr_bottom"]),
            "relative_reduction": float(early_effect["relative_reduction"]),
            "relative_reduction_pct": float(early_effect["relative_reduction_pct"]),
            "absolute_reduction": float(early_effect["absolute_reduction"]),
            "ci_lower": float(early_effect["ci_lower"]),
            "ci_upper": float(early_effect["ci_upper"]),
            "n_bootstrap": int(early_effect["n_boot"]),
        },
        "full_sample_effect_pct": float(FULL_SAMPLE_EFFECT_PCT),
        "persistence_ratio": float(persistence_ratio),
        "sample_validation": {k: (int(v) if isinstance(v, (int, np.integer)) else bool(v) if isinstance(v, (bool, np.bool_)) else v) for k, v in sample_validation.items()},
        "thresholds": {
            "relative_reduction_min": float(RELATIVE_REDUCTION_MIN),
            "persistence_ratio_min": float(PERSISTENCE_RATIO_MIN),
        },
        "interpretation": (
            "PASS: Metadata effect persists in early runs; reverse causality ruled out"
            if gate_pass else
            "FAIL: Effect may be due to community convergence; causal claim weakened"
        ),
    }

    with open(PATHS["effects"], "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved results to {PATHS['effects']}")

    # Generate figures
    print("\nGenerating figures...")
    plot_effect_comparison(early_effect, PATHS["figures_dir"])
    plot_temporal_decay(runs_df, PATHS["figures_dir"])

    print("\n" + "=" * 60)
    print("h-c1 COMPLETE")
    print("=" * 60)

    return results


if __name__ == "__main__":
    main()
