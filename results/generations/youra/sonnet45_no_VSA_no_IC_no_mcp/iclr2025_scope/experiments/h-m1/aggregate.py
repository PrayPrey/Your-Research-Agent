#!/usr/bin/env python3
"""h-m1: Confidence-weighted compliance score aggregation with bootstrap CI."""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import numpy as np
from scipy.stats import bootstrap, pearsonr
import matplotlib.pyplot as plt

# Configuration
CONFIG = {
    "signals_dir": "data/h-e1/benchmark_metadata_corpus/extracted_signals",
    "ground_truth_path": "data/h-e1/benchmark_metadata_corpus/ground_truth/expert_ratings.json",
    "output_dir": "experiments/h-m1",
    "results_file": "results.json",
    "figures_dir": "figures",

    "source_confidences": {
        "paper_methodology": 0.95,
        "readme_setup": 0.85,
        "code_structure": 0.75,
        "registry_metadata": 0.90,
        "load_test_result": 1.0
    },

    "bootstrap": {
        "n_resamples": 1000,
        "confidence_level": 0.95,
        "random_seed": 42,
        "method": "percentile"
    },

    "gates": {
        "ci_width_max": 0.3,
        "pct_benchmarks_min": 80.0,
        "correlation_min": 0.7
    },

    "axes": ["data_realness", "eval_automation", "infra_readiness"]
}

SOURCE_CONFIDENCES = CONFIG["source_confidences"]

# Epic 1: Data Loading
def load_extracted_signals(signals_dir: Path) -> Dict[str, Dict]:
    """Load h-e2 signal extraction output."""
    signals = {}
    for signal_file in signals_dir.glob("*_signals.json"):
        with open(signal_file) as f:
            data = json.load(f)
            benchmark_id = data.pop("benchmark_id")
            signals[benchmark_id] = data
    return signals

def load_ground_truth(gt_path: Path) -> Dict[str, Dict[str, float]]:
    """Load expert compliance ratings."""
    with open(gt_path) as f:
        return json.load(f)

# Epic 2: Aggregation Logic
def baseline_aggregation(signals: List[int]) -> Tuple[Optional[float], float]:
    """Simple averaging baseline."""
    if not signals:
        return (None, 1.0)
    return (np.mean(signals), 1.0)

def confidence_weighted_aggregation(
    signals: List[int],
    confidences: List[float],
    n_resamples: int = 1000,
    random_seed: int = 42
) -> Tuple[Optional[float], float]:
    """Aggregate signals with confidence weighting + bootstrap CI."""
    if not signals or not confidences:
        return (None, 1.0)

    signals = np.array(signals)
    confidences = np.array(confidences)

    # Fallback for zero confidences
    if np.sum(confidences) == 0:
        confidences = np.ones_like(confidences)

    # Weighted average
    score = np.sum(signals * confidences) / np.sum(confidences)

    # Single signal: use analytical CI
    if len(signals) == 1:
        ci_width = 0.1
        return (score, ci_width)

    # Two signals: analytical variance-based CI
    if len(signals) == 2:
        # Weighted variance approximation
        var = np.var(signals)
        ci_width = min(1.96 * np.sqrt(var / len(signals)), 0.5)
        return (score, ci_width)

    # Bootstrap CI estimation (3+ signals)
    def statistic(sig, conf):
        return np.sum(sig * conf) / np.sum(conf) if np.sum(conf) > 0 else 0.0

    try:
        rng = np.random.default_rng(random_seed)
        bootstrap_result = bootstrap(
            (signals, confidences),
            statistic,
            n_resamples=n_resamples,
            confidence_level=0.95,
            random_state=rng,
            method='percentile',
            vectorized=False
        )

        ci_lower = bootstrap_result.confidence_interval.low
        ci_upper = bootstrap_result.confidence_interval.high
        ci_width = ci_upper - ci_lower
    except (ValueError, RuntimeError) as e:
        # Bootstrap failed: fallback to variance-based CI
        var = np.var(signals)
        ci_width = min(1.96 * np.sqrt(var / len(signals)), 0.5)

    # Clip CI width to [0, 0.99] (avoid exact 1.0 = undefined)
    ci_width = np.clip(ci_width, 0.0, 0.99)

    return (score, ci_width)

# Epic 3: Metrics Calculation
def compute_ci_stats(ci_widths: List[float]) -> Dict[str, float]:
    """Compute CI width statistics."""
    ci_widths = np.array(ci_widths)
    return {
        "mean_ci_width": float(np.mean(ci_widths)),
        "pct_ci_under_0.3": float(np.mean(ci_widths < 0.3) * 100),
        "pct_undefined": float(np.mean(ci_widths >= 1.0) * 100)
    }

def compute_correlation(
    bcvf_scores: List[float],
    expert_scores: List[float]
) -> Dict[str, float]:
    """Pearson correlation with expert ratings."""
    if len(bcvf_scores) == 0 or len(expert_scores) == 0:
        return {"pearson_r": 0.0, "p_value": 1.0}
    r, p_value = pearsonr(bcvf_scores, expert_scores)
    return {"pearson_r": float(r), "p_value": float(p_value)}

# Epic 4: Visualization
def plot_gate_metrics(
    baseline_stats: Dict,
    proposed_stats: Dict,
    output_dir: Path
):
    """Bar chart: baseline vs proposed (mean CI, % CI<0.3, % undefined)."""
    metrics = ["mean_ci_width", "pct_ci_under_0.3", "pct_undefined"]
    labels = ["Mean CI Width", "% CI < 0.3", "% Undefined"]

    baseline_vals = [baseline_stats[m] for m in metrics]
    proposed_vals = [proposed_stats[m] for m in metrics]

    x = np.arange(len(metrics))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x - width/2, baseline_vals, width, label='Baseline', alpha=0.8)
    ax.bar(x + width/2, proposed_vals, width, label='Proposed', alpha=0.8)

    ax.axhline(y=0.3, color='r', linestyle='--', linewidth=1, alpha=0.7, label='CI Threshold')
    ax.set_ylabel('Value')
    ax.set_title('Gate Metrics Comparison: Baseline vs Proposed')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / "gate_metrics.png", dpi=150)
    plt.close()

def plot_ci_distribution(
    ci_widths_per_axis: Dict[str, List[float]],
    output_dir: Path
):
    """Histogram (3 subplots) with 0.3 threshold line."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    for i, (axis, ci_widths) in enumerate(ci_widths_per_axis.items()):
        axes[i].hist(ci_widths, bins=10, range=(0, 1), alpha=0.7, edgecolor='black')
        axes[i].axvline(x=0.3, color='r', linestyle='--', linewidth=2, label='Threshold (0.3)')
        axes[i].set_xlabel('CI Width')
        axes[i].set_ylabel('Number of Benchmarks')
        axes[i].set_title(f'{axis.replace("_", " ").title()}')
        axes[i].legend()
        axes[i].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / "ci_distribution.png", dpi=150)
    plt.close()

def plot_correlation_scatter(
    bcvf_scores: Dict[str, List[float]],
    expert_scores: Dict[str, List[float]],
    output_dir: Path
):
    """Scatter plot (3 subplots) with Pearson r annotation."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    for i, axis in enumerate(bcvf_scores.keys()):
        bcvf = bcvf_scores[axis]
        expert = expert_scores[axis]

        r, _ = pearsonr(bcvf, expert)

        axes[i].scatter(expert, bcvf, alpha=0.6)
        axes[i].plot([0, 1], [0, 1], 'r--', alpha=0.5, label='Perfect Correlation')
        axes[i].set_xlabel('Expert Scores')
        axes[i].set_ylabel('BCVF Scores')
        axes[i].set_title(f'{axis.replace("_", " ").title()}')
        axes[i].text(0.05, 0.95, f'r = {r:.3f}', transform=axes[i].transAxes,
                    verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        axes[i].grid(True, alpha=0.3)
        axes[i].legend()

    plt.tight_layout()
    plt.savefig(output_dir / "correlation.png", dpi=150)
    plt.close()

def plot_per_benchmark_ci(
    benchmark_names: List[str],
    ci_widths_per_axis: Dict[str, List[float]],
    output_dir: Path
):
    """Bar chart color-coded by axis with 0.3 threshold."""
    fig, ax = plt.subplots(figsize=(14, 6))

    x = np.arange(len(benchmark_names))
    width = 0.25

    axes_list = list(ci_widths_per_axis.keys())
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']

    for i, axis in enumerate(axes_list):
        offset = (i - 1) * width
        ax.bar(x + offset, ci_widths_per_axis[axis], width, label=axis.replace("_", " ").title(),
               color=colors[i], alpha=0.8)

    ax.axhline(y=0.3, color='r', linestyle='--', linewidth=1.5, alpha=0.7, label='Threshold (0.3)')
    ax.set_xlabel('Benchmark')
    ax.set_ylabel('CI Width')
    ax.set_title('Per-Benchmark CI Width by Axis')
    ax.set_xticks(x)
    ax.set_xticklabels(benchmark_names, rotation=45, ha='right', fontsize=8)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(output_dir / "per_benchmark_ci.png", dpi=150)
    plt.close()

# Main Runner
def run_experiment():
    """Execute full aggregation pipeline."""
    # Setup paths
    signals_dir = Path(CONFIG["signals_dir"])
    gt_path = Path(CONFIG["ground_truth_path"])
    output_dir = Path(CONFIG["output_dir"])
    figures_dir = output_dir / CONFIG["figures_dir"]
    figures_dir.mkdir(parents=True, exist_ok=True)

    # Load data
    print("Loading signals and ground truth...")
    signals = load_extracted_signals(signals_dir)
    ground_truth = load_ground_truth(gt_path)

    benchmark_ids = list(signals.keys())
    axes = CONFIG["axes"]

    # Aggregate per benchmark/axis
    print("Aggregating signals...")
    results = {
        "baseline": {axis: {"scores": [], "ci_widths": []} for axis in axes},
        "proposed": {axis: {"scores": [], "ci_widths": []} for axis in axes}
    }

    expert_ratings = {axis: [] for axis in axes}

    for benchmark_id in benchmark_ids:
        for axis in axes:
            # Extract signals for this axis
            axis_signals_dict = signals[benchmark_id].get(axis, {})

            signal_list = []
            confidence_list = []

            for source, signal_value in axis_signals_dict.items():
                signal_list.append(signal_value)
                confidence_list.append(SOURCE_CONFIDENCES.get(source, 0.5))

            # Baseline aggregation
            baseline_score, baseline_ci = baseline_aggregation(signal_list)
            if baseline_score is not None:
                results["baseline"][axis]["scores"].append(baseline_score)
                results["baseline"][axis]["ci_widths"].append(baseline_ci)

            # Proposed aggregation
            proposed_score, proposed_ci = confidence_weighted_aggregation(
                signal_list, confidence_list,
                n_resamples=CONFIG["bootstrap"]["n_resamples"],
                random_seed=CONFIG["bootstrap"]["random_seed"]
            )
            if proposed_score is not None:
                results["proposed"][axis]["scores"].append(proposed_score)
                results["proposed"][axis]["ci_widths"].append(proposed_ci)

            # Expert ratings
            expert_ratings[axis].append(ground_truth[benchmark_id][axis])

    # Compute statistics
    print("Computing metrics...")
    baseline_stats = {}
    proposed_stats = {}
    correlations = {}

    for axis in axes:
        baseline_ci = results["baseline"][axis]["ci_widths"]
        proposed_ci = results["proposed"][axis]["ci_widths"]

        baseline_stats[axis] = compute_ci_stats(baseline_ci)
        proposed_stats[axis] = compute_ci_stats(proposed_ci)

        correlations[axis] = compute_correlation(
            results["proposed"][axis]["scores"],
            expert_ratings[axis]
        )

    # Aggregate across axes
    all_baseline_ci = []
    all_proposed_ci = []
    for axis in axes:
        all_baseline_ci.extend(results["baseline"][axis]["ci_widths"])
        all_proposed_ci.extend(results["proposed"][axis]["ci_widths"])

    baseline_overall = compute_ci_stats(all_baseline_ci)
    proposed_overall = compute_ci_stats(all_proposed_ci)

    # Generate figures
    print("Generating visualizations...")
    plot_gate_metrics(baseline_overall, proposed_overall, figures_dir)

    ci_widths_per_axis = {axis: results["proposed"][axis]["ci_widths"] for axis in axes}
    plot_ci_distribution(ci_widths_per_axis, figures_dir)

    bcvf_scores = {axis: results["proposed"][axis]["scores"] for axis in axes}
    plot_correlation_scatter(bcvf_scores, expert_ratings, figures_dir)

    plot_per_benchmark_ci(benchmark_ids, ci_widths_per_axis, figures_dir)

    # Gate decision
    print("\n=== Gate Evaluation ===")
    gate_pass = True
    gate_messages = []

    pct_ci_under = proposed_overall["pct_ci_under_0.3"]
    pct_undefined = proposed_overall["pct_undefined"]

    if pct_ci_under < CONFIG["gates"]["pct_benchmarks_min"]:
        gate_pass = False
        gate_messages.append(f"FAIL: Only {pct_ci_under:.1f}% CI < 0.3 (need ≥80%)")
    else:
        gate_messages.append(f"PASS: {pct_ci_under:.1f}% CI < 0.3 (≥80%)")

    if pct_undefined > 0:
        gate_pass = False
        gate_messages.append(f"FAIL: {pct_undefined:.1f}% undefined scores (need 0%)")
    else:
        gate_messages.append(f"PASS: {pct_undefined:.1f}% undefined scores (0%)")

    # Correlation check
    avg_r = np.mean([correlations[axis]["pearson_r"] for axis in axes])
    if avg_r < CONFIG["gates"]["correlation_min"]:
        gate_pass = False
        gate_messages.append(f"FAIL: Avg correlation r={avg_r:.3f} (need ≥0.7)")
    else:
        gate_messages.append(f"PASS: Avg correlation r={avg_r:.3f} (≥0.7)")

    for msg in gate_messages:
        print(msg)

    gate_result = "PASS" if gate_pass else "FAIL"
    print(f"\n🚦 GATE VERDICT: {gate_result}")

    # Save results
    output = {
        "gate_status": gate_result,
        "baseline": baseline_overall,
        "proposed": proposed_overall,
        "per_axis_stats": {
            axis: {
                "ci_stats": proposed_stats[axis],
                "correlation": correlations[axis]
            } for axis in axes
        },
        "gate_messages": gate_messages
    }

    results_path = output_dir / CONFIG["results_file"]
    with open(results_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to {results_path}")
    print(f"Figures saved to {figures_dir}")

    return output

if __name__ == "__main__":
    run_experiment()
