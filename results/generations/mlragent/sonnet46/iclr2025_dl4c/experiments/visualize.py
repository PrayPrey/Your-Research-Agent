"""
Visualization script for HierAlign experiment results.
Generates all figures for the paper.
"""

import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "results"
FIGURES_DIR = RESULTS_DIR / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

REWARD_MODEL_NAMES = {
    "binary": "Binary (Pass/Fail)",
    "syntax_only": "Syntax Only",
    "coverage": "Coverage",
    "hierarchical": "HierAlign (Full)",
}

COLORS = {
    "binary": "#e74c3c",
    "syntax_only": "#e67e22",
    "coverage": "#3498db",
    "hierarchical": "#2ecc71",
}

QUALITY_COLORS = {
    "high": "#2ecc71",
    "medium": "#f39c12",
    "low": "#e74c3c",
}


def load_results():
    results_path = RESULTS_DIR / "experiment_results.json"
    with open(results_path) as f:
        return json.load(f)


def plot_reward_by_quality_level(results_data):
    """
    Figure 1: Reward distributions by quality level for each reward model.
    Shows that hierarchical reward better separates quality levels.
    """
    solutions = results_data["solutions"]
    rm_names = list(REWARD_MODEL_NAMES.keys())

    fig, axes = plt.subplots(1, len(rm_names), figsize=(16, 5))

    for ax, rm_name in zip(axes, rm_names):
        rewards_by_level = {"high": [], "medium": [], "low": []}
        for sol in solutions:
            level = sol["quality_level"]
            reward = sol["rewards"][rm_name]["reward"]
            rewards_by_level[level].append(reward)

        levels = ["high", "medium", "low"]
        positions = [3, 2, 1]
        data = [rewards_by_level[l] for l in levels]
        labels = ["High Quality", "Medium Quality", "Low Quality"]
        colors = [QUALITY_COLORS[l] for l in levels]

        bp = ax.boxplot(data, positions=positions, vert=True, patch_artist=True,
                        widths=0.5, showfliers=True)

        for patch, color in zip(bp["boxes"], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)

        # Add scatter points
        for pos, d, color in zip(positions, data, colors):
            jitter = np.random.uniform(-0.15, 0.15, len(d))
            ax.scatter([pos + j for j in jitter], d, color=color,
                      alpha=0.6, s=20, zorder=3)

        ax.set_title(REWARD_MODEL_NAMES[rm_name], fontsize=12, fontweight='bold')
        ax.set_xlabel("Solution Quality", fontsize=10)
        ax.set_ylabel("Reward Score", fontsize=10)
        ax.set_ylim(-0.05, 1.05)
        ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
        ax.set_xticks(positions)
        ax.set_xticklabels(["High", "Medium", "Low"], fontsize=9)
        ax.grid(axis='y', linestyle='--', alpha=0.4)
        ax.set_facecolor('#f8f9fa')

    fig.suptitle("Reward Score Distribution by Solution Quality Level\n"
                 "(Higher separation = better discriminability)",
                 fontsize=13, fontweight='bold', y=1.02)
    plt.tight_layout()

    path = FIGURES_DIR / "reward_by_quality_level.png"
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved: {path}")
    return str(path)


def plot_discriminability_comparison(results_data):
    """
    Figure 2: Discriminability metrics comparison across reward models.
    Bar chart showing Cohen's d and Kendall-tau for each model.
    """
    metrics = results_data["discriminability_metrics"]
    rm_names = list(REWARD_MODEL_NAMES.keys())

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Cohen's d
    ax = axes[0]
    cohen_d_vals = [metrics[rm]["cohen_d"] for rm in rm_names]
    bars = ax.bar(range(len(rm_names)), cohen_d_vals,
                  color=[COLORS[rm] for rm in rm_names], alpha=0.8, edgecolor='black')
    ax.set_xticks(range(len(rm_names)))
    ax.set_xticklabels([REWARD_MODEL_NAMES[rm] for rm in rm_names],
                       rotation=15, ha='right', fontsize=9)
    ax.set_ylabel("Cohen's d (Effect Size)", fontsize=11)
    ax.set_title("Discriminability: Cohen's d\n(High/Low Quality Separation)",
                 fontsize=11, fontweight='bold')
    ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.6, label='Medium effect')
    ax.axhline(y=0.8, color='gray', linestyle=':', alpha=0.6, label='Large effect')
    ax.legend(fontsize=8)
    for bar, val in zip(bars, cohen_d_vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{val:.3f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax.set_ylim(bottom=min(0, min(cohen_d_vals) - 0.1))
    ax.grid(axis='y', linestyle='--', alpha=0.3)

    # Kendall-tau
    ax = axes[1]
    tau_vals = [metrics[rm]["kendall_tau"] for rm in rm_names]
    bars = ax.bar(range(len(rm_names)), tau_vals,
                  color=[COLORS[rm] for rm in rm_names], alpha=0.8, edgecolor='black')
    ax.set_xticks(range(len(rm_names)))
    ax.set_xticklabels([REWARD_MODEL_NAMES[rm] for rm in rm_names],
                       rotation=15, ha='right', fontsize=9)
    ax.set_ylabel("Kendall's tau", fontsize=11)
    ax.set_title("Rank Correlation with Quality\n(Kendall's tau)",
                 fontsize=11, fontweight='bold')
    ax.axhline(y=0.0, color='black', linestyle='-', alpha=0.3)
    for bar, val in zip(bars, tau_vals):
        y_pos = bar.get_height() + 0.01 if val >= 0 else bar.get_height() - 0.04
        ax.text(bar.get_x() + bar.get_width()/2, y_pos,
                f'{val:.3f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax.set_ylim(-0.1, 1.0)
    ax.grid(axis='y', linestyle='--', alpha=0.3)

    # Reward separation (partial vs full)
    ax = axes[2]
    separation_vals = [metrics[rm]["reward_separation"] for rm in rm_names]
    partial_vals = [metrics[rm]["mean_partial_reward"] for rm in rm_names]
    full_vals = [metrics[rm]["mean_full_reward"] for rm in rm_names]

    x = np.arange(len(rm_names))
    width = 0.35
    b1 = ax.bar(x - width/2, partial_vals, width, label='Partial (0 tests pass)',
                color=[COLORS[rm] for rm in rm_names], alpha=0.5, edgecolor='black',
                hatch='//')
    b2 = ax.bar(x + width/2, full_vals, width, label='Full (all tests pass)',
                color=[COLORS[rm] for rm in rm_names], alpha=0.9, edgecolor='black')
    ax.set_xticks(x)
    ax.set_xticklabels([REWARD_MODEL_NAMES[rm] for rm in rm_names],
                       rotation=15, ha='right', fontsize=9)
    ax.set_ylabel("Mean Reward Score", fontsize=11)
    ax.set_title("Partial vs Full Solution Rewards\n(Gap = useful signal for partial solutions)",
                 fontsize=11, fontweight='bold')
    ax.set_ylim(0, 1.1)
    ax.legend(fontsize=8)
    ax.grid(axis='y', linestyle='--', alpha=0.3)

    plt.suptitle("Reward Model Discriminability Comparison", fontsize=13,
                 fontweight='bold', y=1.02)
    plt.tight_layout()

    path = FIGURES_DIR / "discriminability_comparison.png"
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved: {path}")
    return str(path)


def plot_mean_rewards_by_level(results_data):
    """
    Figure 3: Mean reward by quality level for each reward model (grouped bar chart).
    Shows monotonicity of reward signals.
    """
    metrics = results_data["discriminability_metrics"]
    rm_names = list(REWARD_MODEL_NAMES.keys())

    fig, ax = plt.subplots(figsize=(12, 6))

    levels = ["high", "medium", "low"]
    level_labels = ["High Quality", "Medium Quality", "Low Quality"]
    level_colors = [QUALITY_COLORS[l] for l in levels]

    x = np.arange(len(rm_names))
    width = 0.25

    for i, (level, label, color) in enumerate(zip(levels, level_labels, level_colors)):
        vals = [metrics[rm][f"mean_{level}"] for rm in rm_names]
        offset = (i - 1) * width
        bars = ax.bar(x + offset, vals, width, label=label, color=color,
                      alpha=0.8, edgecolor='black')
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{val:.2f}', ha='center', va='bottom', fontsize=7.5, fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels([REWARD_MODEL_NAMES[rm] for rm in rm_names], fontsize=11)
    ax.set_ylabel("Mean Reward Score", fontsize=12)
    ax.set_xlabel("Reward Model", fontsize=12)
    ax.set_title("Mean Reward Score by Solution Quality Level\n"
                 "(Ideal: High > Medium > Low)", fontsize=13, fontweight='bold')
    ax.set_ylim(0, 1.15)
    ax.legend(fontsize=10, loc='upper right')
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    ax.set_facecolor('#f8f9fa')

    plt.tight_layout()
    path = FIGURES_DIR / "mean_rewards_by_level.png"
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved: {path}")
    return str(path)


def plot_reward_components_ablation(results_data):
    """
    Figure 4: Ablation study - contribution of each hierarchical reward component.
    """
    ablation = results_data["ablation_study"]
    solutions = results_data["solutions"]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Left: Mean component values
    ax = axes[0]
    components = list(ablation.keys())
    comp_labels = {
        "syntax": "L1: Syntactic\nValidity",
        "runtime": "L2: Runtime\nError Class.",
        "coverage": "L3: Partial\nCoverage",
        "semantic": "L4: Semantic\nDistance",
    }
    comp_colors = ["#9b59b6", "#3498db", "#2ecc71", "#e67e22"]

    means = [ablation[c]["mean"] for c in components]
    stds = [ablation[c]["std"] for c in components]
    labels = [comp_labels.get(c, c) for c in components]
    colors = comp_colors[:len(components)]

    bars = ax.bar(range(len(components)), means, yerr=stds, capsize=5,
                  color=colors, alpha=0.8, edgecolor='black')
    ax.set_xticks(range(len(components)))
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel("Mean Component Score", fontsize=11)
    ax.set_title("Mean Score of Each Reward Component\n(HierAlign Ablation)",
                 fontsize=11, fontweight='bold')
    ax.set_ylim(0, 1.15)
    for bar, mean, std in zip(bars, means, stds):
        ax.text(bar.get_x() + bar.get_width()/2, mean + std + 0.02,
                f'{mean:.3f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax.grid(axis='y', linestyle='--', alpha=0.3)

    # Right: Component scores by quality level (stacked)
    ax = axes[1]
    quality_levels = ["high", "medium", "low"]
    comp_by_level = {c: {l: [] for l in quality_levels} for c in components}

    for sol in solutions:
        level = sol["quality_level"]
        hr_result = sol["rewards"]["hierarchical"]
        comps = hr_result.get("components", {})
        for c in components:
            if c in comps:
                comp_by_level[c][level].append(comps[c])

    x = np.arange(len(quality_levels))
    width = 0.18
    offsets = np.linspace(-0.27, 0.27, len(components))

    for comp, offset, color, label in zip(components, offsets, comp_colors, labels):
        vals = [np.mean(comp_by_level[comp][l]) if comp_by_level[comp][l] else 0
                for l in quality_levels]
        ax.bar(x + offset, vals, width, label=label, color=color, alpha=0.8, edgecolor='black')

    ax.set_xticks(x)
    ax.set_xticklabels(["High Quality", "Medium Quality", "Low Quality"], fontsize=10)
    ax.set_ylabel("Mean Component Score", fontsize=11)
    ax.set_title("Reward Components by Quality Level\n(All 4 levels in HierAlign)",
                 fontsize=11, fontweight='bold')
    ax.set_ylim(0, 1.2)
    ax.legend(fontsize=8, loc='upper right')
    ax.grid(axis='y', linestyle='--', alpha=0.3)

    plt.suptitle("HierAlign Component Analysis", fontsize=13, fontweight='bold')
    plt.tight_layout()

    path = FIGURES_DIR / "reward_components_ablation.png"
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved: {path}")
    return str(path)


def plot_reward_guided_selection(results_data):
    """
    Figure 5: Reward-guided selection performance.
    How often does the reward model select the best solution?
    """
    pass_stats = results_data["pass_at_k_stats"]
    rm_names = list(REWARD_MODEL_NAMES.keys())

    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(len(rm_names))
    width = 0.35

    guided_rates = [pass_stats[rm]["reward_guided_correct_rate"] for rm in rm_names]
    random_rates = [pass_stats[rm]["random_selection_rate"] for rm in rm_names]
    improvements = [pass_stats[rm]["improvement_over_random"] for rm in rm_names]

    b1 = ax.bar(x - width/2, random_rates, width, label='Random Selection',
                color='#95a5a6', alpha=0.8, edgecolor='black')
    b2 = ax.bar(x + width/2, guided_rates, width, label='Reward-Guided Selection',
                color=[COLORS[rm] for rm in rm_names], alpha=0.9, edgecolor='black')

    # Add improvement annotations
    for i, (xi, guided, random) in enumerate(zip(x, guided_rates, random_rates)):
        imp = guided - random
        if abs(imp) > 0.001:
            ax.annotate(f'+{imp:.3f}' if imp >= 0 else f'{imp:.3f}',
                       xy=(xi + width/2, guided),
                       xytext=(0, 5), textcoords='offset points',
                       ha='center', fontsize=9, color='#2c3e50', fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels([REWARD_MODEL_NAMES[rm] for rm in rm_names], fontsize=11)
    ax.set_ylabel("Fraction of Problems with Correct Selection", fontsize=11)
    ax.set_xlabel("Reward Model", fontsize=12)
    ax.set_title("Reward-Guided Solution Selection\nvs. Random Selection",
                 fontsize=13, fontweight='bold')
    ax.set_ylim(0, 1.1)
    ax.legend(fontsize=11)
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    ax.set_facecolor('#f8f9fa')

    plt.tight_layout()
    path = FIGURES_DIR / "reward_guided_selection.png"
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved: {path}")
    return str(path)


def plot_per_problem_analysis(results_data):
    """
    Figure 6: Per-problem reward comparison between binary and hierarchical.
    Shows that hierarchical gives gradient signal where binary gives 0.
    """
    solutions = results_data["solutions"]

    # Group by problem and compute statistics
    by_task = {}
    for sol in solutions:
        tid = sol["task_id"]
        if tid not in by_task:
            by_task[tid] = []
        by_task[tid].append(sol)

    task_ids = sorted(by_task.keys())

    # For each problem, compute mean rewards for low-quality solutions
    binary_low = []
    hier_low = []

    for tid in task_ids:
        sols = by_task[tid]
        low_sols = [s for s in sols if s["quality_level"] == "low"]
        if low_sols:
            b_mean = np.mean([s["rewards"]["binary"]["reward"] for s in low_sols])
            h_mean = np.mean([s["rewards"]["hierarchical"]["reward"] for s in low_sols])
            binary_low.append(b_mean)
            hier_low.append(h_mean)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Left: Per-problem comparison for low-quality solutions
    ax = axes[0]
    x = np.arange(len(task_ids))
    ax.scatter(x, binary_low, color=COLORS["binary"], s=60, label='Binary',
               zorder=3, marker='o', alpha=0.8)
    ax.scatter(x, hier_low, color=COLORS["hierarchical"], s=60, label='HierAlign',
               zorder=3, marker='^', alpha=0.8)

    # Connect with lines
    for i, (b, h) in enumerate(zip(binary_low, hier_low)):
        ax.plot([i, i], [b, h], 'k-', alpha=0.2, linewidth=0.8)

    ax.set_xticks(x)
    ax.set_xticklabels([t.replace("HE_", "") for t in task_ids], fontsize=8)
    ax.set_xlabel("Problem ID (HE_N)", fontsize=11)
    ax.set_ylabel("Mean Reward Score (Low Quality Solutions)", fontsize=11)
    ax.set_title("Per-Problem Reward: Low Quality Solutions\n"
                 "(HierAlign provides gradient vs Binary's 0/1 signal)",
                 fontsize=11, fontweight='bold')
    ax.set_ylim(-0.05, 1.05)
    ax.legend(fontsize=10)
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    ax.set_facecolor('#f8f9fa')

    # Right: Scatter plot of binary vs hierarchical reward (all solutions)
    ax = axes[1]
    all_binary = [sol["rewards"]["binary"]["reward"] for sol in solutions]
    all_hier = [sol["rewards"]["hierarchical"]["reward"] for sol in solutions]
    all_levels = [sol["quality_level"] for sol in solutions]

    for level in ["high", "medium", "low"]:
        mask = [l == level for l in all_levels]
        bx = [b for b, m in zip(all_binary, mask) if m]
        hx = [h for h, m in zip(all_hier, mask) if m]
        ax.scatter(bx, hx, color=QUALITY_COLORS[level], alpha=0.6, s=50,
                   label=f'{level.capitalize()} quality',
                   zorder=3)

    ax.plot([0, 1], [0, 1], 'k--', alpha=0.3, linewidth=1, label='y=x')
    ax.set_xlabel("Binary Reward", fontsize=11)
    ax.set_ylabel("HierAlign Reward", fontsize=11)
    ax.set_title("Binary vs HierAlign Rewards\n(All Solutions, colored by quality)",
                 fontsize=11, fontweight='bold')
    ax.set_xlim(-0.05, 1.1)
    ax.set_ylim(-0.05, 1.1)
    ax.legend(fontsize=9)
    ax.grid(linestyle='--', alpha=0.3)
    ax.set_facecolor('#f8f9fa')

    plt.suptitle("Per-Problem Analysis: Binary vs HierAlign Feedback",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()

    path = FIGURES_DIR / "per_problem_analysis.png"
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved: {path}")
    return str(path)


def plot_summary_radar(results_data):
    """
    Figure 7: Radar/spider chart comparing all reward models on key metrics.
    """
    metrics = results_data["discriminability_metrics"]
    rm_names = list(REWARD_MODEL_NAMES.keys())

    # Metrics to compare (normalized to [0,1])
    metric_keys = [
        ("kendall_tau", "Rank Correlation\n(Kendall tau)"),
        ("reward_separation", "Reward\nSeparation"),
        ("cohen_d", "Effect Size\n(Cohen d)"),
    ]

    # Add mean_high - mean_low as a metric
    for rm in rm_names:
        metrics[rm]["high_low_gap"] = metrics[rm]["mean_high"] - metrics[rm]["mean_low"]

    metric_keys.append(("high_low_gap", "High-Low\nGap"))

    # Normalize each metric to [0, 1]
    all_vals = {mk: [max(0, metrics[rm][mk]) for rm in rm_names] for mk, _ in metric_keys}
    max_vals = {mk: max(vals) if max(vals) > 0 else 1 for mk, vals in all_vals.items()}

    N = len(metric_keys)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

    for rm_name in rm_names:
        vals = [max(0, metrics[rm_name][mk]) / max_vals[mk] for mk, _ in metric_keys]
        vals += vals[:1]

        ax.plot(angles, vals, 'o-', linewidth=2, label=REWARD_MODEL_NAMES[rm_name],
                color=COLORS[rm_name])
        ax.fill(angles, vals, alpha=0.1, color=COLORS[rm_name])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([label for _, label in metric_keys], fontsize=11)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(['0.25', '0.5', '0.75', '1.0'], fontsize=8)
    ax.set_title("Reward Model Comparison\n(Normalized metrics, larger = better)",
                 fontsize=13, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.4)

    plt.tight_layout()
    path = FIGURES_DIR / "summary_radar.png"
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved: {path}")
    return str(path)


def generate_all_figures():
    """Generate all experiment figures."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

    logger.info("Loading results...")
    results_data = load_results()

    figures = {}

    logger.info("Generating Figure 1: Reward by quality level...")
    figures["reward_by_quality"] = plot_reward_by_quality_level(results_data)

    logger.info("Generating Figure 2: Discriminability comparison...")
    figures["discriminability"] = plot_discriminability_comparison(results_data)

    logger.info("Generating Figure 3: Mean rewards by level...")
    figures["mean_rewards"] = plot_mean_rewards_by_level(results_data)

    logger.info("Generating Figure 4: Component ablation...")
    figures["ablation"] = plot_reward_components_ablation(results_data)

    logger.info("Generating Figure 5: Reward-guided selection...")
    figures["selection"] = plot_reward_guided_selection(results_data)

    logger.info("Generating Figure 6: Per-problem analysis...")
    figures["per_problem"] = plot_per_problem_analysis(results_data)

    logger.info("Generating Figure 7: Summary radar...")
    figures["radar"] = plot_summary_radar(results_data)

    logger.info(f"\nAll figures saved to {FIGURES_DIR}")
    return figures


if __name__ == "__main__":
    generate_all_figures()
