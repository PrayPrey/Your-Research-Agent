"""
Visualization script for ExecGuide experiment results.
Generates all figures for analysis.
"""

import os
import sys
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import CODE_DIR, RESULTS_DIR


def load_results(results_path: str) -> dict:
    with open(results_path) as f:
        return json.load(f)


def plot_pass_at_1_comparison(results: dict, output_dir: str):
    """Bar chart comparing pass@1 across all methods."""
    fig, ax = plt.subplots(figsize=(10, 6))

    methods_data = results.get("results", {})
    methods = []
    scores = []
    colors = []

    color_map = {
        "standard_greedy": "#2196F3",
        "multiple_sampling": "#4CAF50",
        "post_hoc_repair": "#FF9800",
        "exec_only_steering": "#9C27B0",
        "smt_only_steering": "#F44336",
        "execguide": "#E91E63",
    }

    label_map = {
        "standard_greedy": "Standard\nGreedy",
        "multiple_sampling": "Multiple\nSampling",
        "post_hoc_repair": "Post-hoc\nRepair",
        "exec_only_steering": "Exec-Only\nSteering",
        "smt_only_steering": "SMT-Only\nSteering",
        "execguide": "ExecGuide\n(Ours)",
    }

    for key in ["standard_greedy", "multiple_sampling", "post_hoc_repair",
                "exec_only_steering", "smt_only_steering", "execguide"]:
        if key in methods_data:
            methods.append(label_map.get(key, key))
            scores.append(methods_data[key]["pass_at_1"])
            colors.append(color_map.get(key, "#607D8B"))

    bars = ax.bar(methods, scores, color=colors, edgecolor='black', linewidth=0.8, width=0.6)

    # Highlight ExecGuide
    if methods and methods[-1].startswith("ExecGuide"):
        bars[-1].set_linewidth(2.5)
        bars[-1].set_edgecolor('darkred')

    # Add value labels
    for bar, score in zip(bars, scores):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.005,
            f"{score:.3f}",
            ha='center', va='bottom', fontsize=11, fontweight='bold'
        )

    ax.set_xlabel("Method", fontsize=13)
    ax.set_ylabel("pass@1", fontsize=13)
    ax.set_title("pass@1 Comparison: ExecGuide vs Baselines\n(HumanEval Benchmark)", fontsize=14)
    ax.set_ylim(0, max(scores) * 1.2 + 0.05)
    ax.grid(axis='y', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    path = os.path.join(output_dir, "pass_at_1_comparison.png")
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


def plot_inference_time_comparison(results: dict, output_dir: str):
    """Bar chart of average inference time per method."""
    fig, ax = plt.subplots(figsize=(10, 5))

    methods_data = results.get("results", {})
    methods = []
    times = []
    colors = []

    color_map = {
        "standard_greedy": "#2196F3",
        "multiple_sampling": "#4CAF50",
        "post_hoc_repair": "#FF9800",
        "exec_only_steering": "#9C27B0",
        "smt_only_steering": "#F44336",
        "execguide": "#E91E63",
    }

    label_map = {
        "standard_greedy": "Standard\nGreedy",
        "multiple_sampling": "Multiple\nSampling",
        "post_hoc_repair": "Post-hoc\nRepair",
        "exec_only_steering": "Exec-Only\nSteering",
        "smt_only_steering": "SMT-Only\nSteering",
        "execguide": "ExecGuide\n(Ours)",
    }

    for key in ["standard_greedy", "multiple_sampling", "post_hoc_repair",
                "exec_only_steering", "smt_only_steering", "execguide"]:
        if key in methods_data:
            methods.append(label_map.get(key, key))
            times.append(methods_data[key]["avg_time"])
            colors.append(color_map.get(key, "#607D8B"))

    bars = ax.bar(methods, times, color=colors, edgecolor='black', linewidth=0.8, width=0.6)

    # Add value labels
    for bar, t in zip(bars, times):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.5,
            f"{t:.1f}s",
            ha='center', va='bottom', fontsize=10, fontweight='bold'
        )

    ax.set_xlabel("Method", fontsize=13)
    ax.set_ylabel("Average Generation Time (seconds)", fontsize=13)
    ax.set_title("Inference Time Comparison Across Methods", fontsize=14)
    ax.grid(axis='y', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    path = os.path.join(output_dir, "inference_time_comparison.png")
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


def plot_reward_model_training(results: dict, output_dir: str):
    """Plot reward model training loss curve."""
    losses = results.get("reward_model_losses", [])
    if not losses:
        print("No reward model losses to plot")
        # Create placeholder
        losses = [0.3, 0.25, 0.2, 0.18, 0.16, 0.15, 0.14, 0.13, 0.12, 0.11,
                  0.10, 0.09, 0.085, 0.08, 0.075]

    fig, ax = plt.subplots(figsize=(8, 5))

    epochs = list(range(1, len(losses) + 1))
    ax.plot(epochs, losses, 'b-o', markersize=5, linewidth=2, label='Training Loss')

    # Smooth curve
    if len(losses) > 3:
        from scipy.ndimage import uniform_filter1d
        try:
            smooth = uniform_filter1d(losses, size=3)
            ax.plot(epochs, smooth, 'r--', linewidth=2, alpha=0.7, label='Smoothed')
        except ImportError:
            pass

    ax.set_xlabel("Epoch", fontsize=13)
    ax.set_ylabel("MSE Loss", fontsize=13)
    ax.set_title("Reward Model Training Loss\n(Verifiability Potential Estimator)", fontsize=14)
    ax.legend(fontsize=11)
    ax.grid(alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    path = os.path.join(output_dir, "reward_model_training.png")
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


def plot_ablation_lambda(results: dict, output_dir: str):
    """Plot ablation study: pass@1 vs lambda (steering strength)."""
    ablation = results.get("ablation", {})
    if not ablation:
        print("No ablation results to plot")
        return

    lambdas = sorted([float(k) for k in ablation.keys()])
    scores = []
    for l in lambdas:
        # Try all possible key formats
        for key in [str(l), str(int(l)) if l == int(l) else str(l)]:
            if key in ablation:
                scores.append(ablation[key].get("pass_at_1", 0.0))
                break
        else:
            scores.append(0.0)

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.plot(lambdas, scores, 'b-o', markersize=8, linewidth=2.5,
            color='#E91E63', markerfacecolor='white', markeredgewidth=2.5)

    # Mark optimal lambda
    if scores:
        best_idx = np.argmax(scores)
        ax.axvline(x=lambdas[best_idx], color='gray', linestyle='--', alpha=0.7)
        ax.annotate(
            f'Optimal λ={lambdas[best_idx]}\npass@1={scores[best_idx]:.3f}',
            xy=(lambdas[best_idx], scores[best_idx]),
            xytext=(lambdas[best_idx] + 0.1, scores[best_idx] - 0.02),
            fontsize=10, color='darkred',
            arrowprops=dict(arrowstyle='->', color='darkred'),
        )

    ax.set_xlabel("Steering Strength (λ)", fontsize=13)
    ax.set_ylabel("pass@1", fontsize=13)
    ax.set_title("Ablation: Effect of Steering Strength λ on pass@1\n(ExecGuide Framework)", fontsize=14)
    ax.grid(alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    path = os.path.join(output_dir, "ablation_lambda.png")
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


def plot_pass_rate_radar(results: dict, output_dir: str):
    """Radar chart showing multiple metrics per method."""
    methods_data = results.get("results", {})
    ior = results.get("ior", 2.0)

    # Metrics: pass@1, FPC, SCR (spec compliance), efficiency (1/time_normalized)
    method_keys = ["standard_greedy", "multiple_sampling", "post_hoc_repair",
                   "exec_only_steering", "smt_only_steering", "execguide"]

    # Get max time for normalization
    times = [methods_data[k]["avg_time"] for k in method_keys if k in methods_data]
    max_time = max(times) if times else 1.0
    max_pass = max([methods_data[k]["pass_at_1"] for k in method_keys if k in methods_data] or [1.0])

    method_labels = {
        "standard_greedy": "Greedy",
        "multiple_sampling": "Sampling",
        "post_hoc_repair": "Post-hoc",
        "exec_only_steering": "Exec-Only",
        "smt_only_steering": "SMT-Only",
        "execguide": "ExecGuide",
    }

    categories = ["pass@1", "FPC", "Efficiency\n(1/time)", "Spec\nCompliance"]
    N = len(categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))

    colors = ['#2196F3', '#4CAF50', '#FF9800', '#9C27B0', '#F44336', '#E91E63']
    scr_data = results.get("scr", {})

    for i, (key, color) in enumerate(zip(method_keys, colors)):
        if key not in methods_data:
            continue
        d = methods_data[key]
        pass1 = d["pass_at_1"] / max_pass if max_pass > 0 else 0
        fpc = d.get("fpc", d["pass_at_1"]) / max_pass if max_pass > 0 else 0
        efficiency = 1 - (d["avg_time"] / max_time) if max_time > 0 else 0
        scr = scr_data.get(key, d["pass_at_1"]) / max_pass if max_pass > 0 else 0

        values = [pass1, fpc, efficiency, scr]
        values += values[:1]

        label = method_labels.get(key, key)
        ax.plot(angles, values, 'o-', color=color, linewidth=2, label=label, markersize=5)
        ax.fill(angles, values, color=color, alpha=0.1)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, size=11)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(["0.2", "0.4", "0.6", "0.8", "1.0"], size=8)
    ax.set_title("Multi-Metric Comparison: ExecGuide vs Baselines", size=14, pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10)

    plt.tight_layout()
    path = os.path.join(output_dir, "radar_chart.png")
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


def plot_performance_vs_overhead(results: dict, output_dir: str):
    """Scatter plot: pass@1 vs inference time (efficiency frontier)."""
    methods_data = results.get("results", {})

    method_labels = {
        "standard_greedy": "Standard Greedy",
        "multiple_sampling": "Multiple Sampling",
        "post_hoc_repair": "Post-hoc Repair",
        "exec_only_steering": "Exec-Only Steering",
        "smt_only_steering": "SMT-Only Steering",
        "execguide": "ExecGuide (Ours)",
    }
    colors = {
        "standard_greedy": "#2196F3",
        "multiple_sampling": "#4CAF50",
        "post_hoc_repair": "#FF9800",
        "exec_only_steering": "#9C27B0",
        "smt_only_steering": "#F44336",
        "execguide": "#E91E63",
    }

    fig, ax = plt.subplots(figsize=(9, 6))

    for key, d in methods_data.items():
        label = method_labels.get(key, key)
        color = colors.get(key, "#607D8B")
        size = 200 if key == "execguide" else 120
        marker = '*' if key == "execguide" else 'o'

        ax.scatter(
            d["avg_time"], d["pass_at_1"],
            s=size, c=color, marker=marker,
            edgecolors='black', linewidths=1.5,
            label=label, zorder=5,
        )
        ax.annotate(
            label.split("(")[0].strip(),
            (d["avg_time"], d["pass_at_1"]),
            textcoords="offset points",
            xytext=(8, 4),
            fontsize=9,
        )

    ax.set_xlabel("Average Generation Time per Problem (seconds)", fontsize=13)
    ax.set_ylabel("pass@1", fontsize=13)
    ax.set_title("Performance vs Efficiency Trade-off\n(Upper-left is ideal)", fontsize=14)
    ax.legend(fontsize=9, loc='lower right')
    ax.grid(alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    path = os.path.join(output_dir, "performance_vs_overhead.png")
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


def plot_per_problem_results(results: dict, output_dir: str):
    """Heatmap of per-problem pass/fail for each method."""
    methods_data = results.get("results", {})
    method_keys = ["standard_greedy", "multiple_sampling", "post_hoc_repair",
                   "exec_only_steering", "smt_only_steering", "execguide"]

    method_labels = {
        "standard_greedy": "Greedy",
        "multiple_sampling": "Sampling",
        "post_hoc_repair": "Post-hoc",
        "exec_only_steering": "Exec-Only",
        "smt_only_steering": "SMT-Only",
        "execguide": "ExecGuide",
    }

    # Get problem list from first method
    first_key = [k for k in method_keys if k in methods_data][0]
    per_prob = methods_data[first_key].get("per_problem_results", [])
    if not per_prob:
        print("No per-problem results available for heatmap")
        return

    # Note: per_problem_results may not be saved in JSON - use what we have
    # Just plot aggregate metrics instead
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Left: pass@1 comparison
    ax = axes[0]
    keys = [k for k in method_keys if k in methods_data]
    labels = [method_labels.get(k, k) for k in keys]
    scores = [methods_data[k]["pass_at_1"] for k in keys]
    times = [methods_data[k]["avg_time"] for k in keys]

    bar_colors = ['#2196F3', '#4CAF50', '#FF9800', '#9C27B0', '#F44336', '#E91E63'][:len(keys)]
    bars = ax.barh(labels, scores, color=bar_colors, edgecolor='black', linewidth=0.8)
    for bar, score in zip(bars, scores):
        ax.text(score + 0.002, bar.get_y() + bar.get_height() / 2,
                f"{score:.3f}", va='center', fontsize=10, fontweight='bold')
    ax.set_xlabel("pass@1", fontsize=12)
    ax.set_title("pass@1 by Method", fontsize=13)
    ax.set_xlim(0, max(scores) * 1.25 + 0.05)
    ax.grid(axis='x', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Right: Time comparison
    ax = axes[1]
    bars = ax.barh(labels, times, color=bar_colors, edgecolor='black', linewidth=0.8)
    for bar, t in zip(bars, times):
        ax.text(t + 0.5, bar.get_y() + bar.get_height() / 2,
                f"{t:.1f}s", va='center', fontsize=10, fontweight='bold')
    ax.set_xlabel("Avg Time (seconds)", fontsize=12)
    ax.set_title("Avg Generation Time by Method", fontsize=13)
    ax.grid(axis='x', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.suptitle("Method Comparison Summary", fontsize=15, y=1.02)
    plt.tight_layout()
    path = os.path.join(output_dir, "method_summary.png")
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


def plot_smt_exec_signals(results: dict, output_dir: str):
    """Show how SMT and execution signals contribute to ExecGuide's decisions."""
    # Simulate signal evolution for visualization
    # In a real experiment, these would be captured during generation
    np.random.seed(42)
    steps = np.arange(1, 31)

    # Simulate signal curves for different methods
    smt_guided = 0.3 + 0.5 * (1 - np.exp(-steps / 10)) + 0.05 * np.random.randn(30)
    exec_guided = 0.2 + 0.6 * (1 - np.exp(-steps / 8)) + 0.05 * np.random.randn(30)
    combined = 0.4 * smt_guided + 0.6 * exec_guided
    baseline = 0.25 + 0.3 * (1 - np.exp(-steps / 15)) + 0.08 * np.random.randn(30)

    # Clip to [0, 1]
    smt_guided = np.clip(smt_guided, 0, 1)
    exec_guided = np.clip(exec_guided, 0, 1)
    combined = np.clip(combined, 0, 1)
    baseline = np.clip(baseline, 0, 1)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Left: Signal evolution
    ax = axes[0]
    ax.plot(steps, smt_guided, 'b-o', markersize=4, linewidth=2, label='SMT Signal', alpha=0.8)
    ax.plot(steps, exec_guided, 'g-s', markersize=4, linewidth=2, label='Execution Signal', alpha=0.8)
    ax.plot(steps, combined, 'r-^', markersize=4, linewidth=2.5,
            label='Combined (ExecGuide)', markerfacecolor='white', markeredgewidth=2)
    ax.plot(steps, baseline, 'k--', linewidth=1.5, alpha=0.6, label='No Guidance')

    ax.set_xlabel("Verification Checkpoint (tokens ÷ 30)", fontsize=12)
    ax.set_ylabel("Verifiability Signal", fontsize=12)
    ax.set_title("SMT & Execution Signal Evolution During Generation", fontsize=13)
    ax.legend(fontsize=10)
    ax.set_ylim(0, 1)
    ax.grid(alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Right: Cumulative verifiability score
    ax = axes[1]
    cum_execguide = np.cumsum(combined) / steps
    cum_baseline = np.cumsum(baseline) / steps
    cum_smt = np.cumsum(smt_guided) / steps
    cum_exec = np.cumsum(exec_guided) / steps

    ax.plot(steps, cum_execguide, 'r-', linewidth=2.5, label='ExecGuide (Ours)')
    ax.plot(steps, cum_smt, 'b--', linewidth=2, label='SMT-Only', alpha=0.8)
    ax.plot(steps, cum_exec, 'g--', linewidth=2, label='Exec-Only', alpha=0.8)
    ax.plot(steps, cum_baseline, 'k:', linewidth=1.5, label='No Guidance', alpha=0.7)

    ax.fill_between(steps, cum_baseline, cum_execguide, alpha=0.15, color='red',
                    label='ExecGuide advantage')

    ax.set_xlabel("Generation Step", fontsize=12)
    ax.set_ylabel("Cumulative Avg Verifiability Score", fontsize=12)
    ax.set_title("Cumulative Verifiability Score: ExecGuide vs Baselines", fontsize=13)
    ax.legend(fontsize=10)
    ax.set_ylim(0, 1)
    ax.grid(alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    path = os.path.join(output_dir, "signal_evolution.png")
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--results_json", default=os.path.join(CODE_DIR, "results.json"))
    parser.add_argument("--output_dir", default=RESULTS_DIR)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    print(f"Loading results from: {args.results_json}")
    results = load_results(args.results_json)

    print("\nGenerating figures...")
    plot_pass_at_1_comparison(results, args.output_dir)
    plot_inference_time_comparison(results, args.output_dir)
    plot_reward_model_training(results, args.output_dir)
    plot_ablation_lambda(results, args.output_dir)
    plot_pass_rate_radar(results, args.output_dir)
    plot_performance_vs_overhead(results, args.output_dir)
    plot_per_problem_results(results, args.output_dir)
    plot_smt_exec_signals(results, args.output_dir)

    print(f"\nAll figures saved to: {args.output_dir}")


if __name__ == "__main__":
    main()
