"""Visualization for h-e1 experiment results."""
import json
import os
import matplotlib.pyplot as plt
import numpy as np


def plot_gate_metrics_comparison(steps_gated: int, steps_always: int, path: str):
    """Required figure: Bar chart comparing steps-to-30% for both conditions."""
    fig, ax = plt.subplots(figsize=(8, 6))

    conditions = ['fine_always\n(baseline)', 'fine_gated\n(proposed)']
    steps = [steps_always or 0, steps_gated or 0]
    colors = ['#1f77b4', '#2ca02c']

    bars = ax.bar(conditions, steps, color=colors, edgecolor='black', linewidth=1.2)

    for bar, s in zip(bars, steps):
        if s > 0:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 500,
                    f'{s:,}', ha='center', va='bottom', fontsize=12, fontweight='bold')

    ax.set_ylabel('Training Steps to 30% pass@1', fontsize=12)
    ax.set_title('Error-Type Gating: Sample Efficiency Comparison', fontsize=14, fontweight='bold')
    ax.set_ylim(0, max(steps) * 1.15 if max(steps) > 0 else 1)

    if steps_always and steps_gated:
        improvement = (steps_always - steps_gated) / steps_always * 100
        ax.text(0.95, 0.95, f'Improvement: {improvement:.1f}%',
                transform=ax.transAxes, ha='right', va='top',
                fontsize=11, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


def plot_training_curves(curves: dict, path: str):
    """Training curves: pass@1 vs steps for both conditions."""
    fig, ax = plt.subplots(figsize=(10, 6))

    for condition, data in curves.items():
        steps = [p[0] for p in data]
        p1 = [p[1] for p in data]
        label = 'fine_always (baseline)' if condition == 'fine_always' else 'fine_gated (proposed)'
        color = '#1f77b4' if condition == 'fine_always' else '#2ca02c'
        ax.plot(steps, p1, marker='o', label=label, color=color, linewidth=2, markersize=6)

    ax.axhline(y=0.30, color='red', linestyle='--', linewidth=1.5, label='30% threshold')

    ax.set_xlabel('Training Steps', fontsize=12)
    ax.set_ylabel('pass@1', fontsize=12)
    ax.set_title('Training Progress: pass@1 vs Steps', fontsize=14, fontweight='bold')
    ax.legend(loc='lower right', fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


def plot_error_distribution(u_line_count: int, u_ignore_count: int, path: str):
    """Pie chart of U_line vs U_ignore errors during training."""
    fig, ax = plt.subplots(figsize=(8, 8))

    sizes = [u_line_count, u_ignore_count]
    labels = [f'U_line\n({u_line_count})', f'U_ignore\n({u_ignore_count})']
    colors = ['#2ca02c', '#d62728']
    explode = (0.02, 0.02)

    if sum(sizes) > 0:
        ax.pie(sizes, labels=labels, colors=colors, explode=explode,
               autopct='%1.1f%%', startangle=90, textprops={'fontsize': 12})
    else:
        ax.text(0.5, 0.5, 'No error data', ha='center', va='center', fontsize=14)

    ax.set_title('Error Distribution During Training', fontsize=14, fontweight='bold')

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


def plot_efficiency_ratio(steps_gated: int, steps_always: int, path: str):
    """Horizontal bar showing % improvement."""
    fig, ax = plt.subplots(figsize=(10, 4))

    if steps_always and steps_gated and steps_always > 0:
        ratio = (steps_always - steps_gated) / steps_always * 100
    else:
        ratio = 0

    color = '#2ca02c' if ratio > 10 else '#ff7f0e' if ratio > 0 else '#d62728'

    ax.barh(['Efficiency\nImprovement'], [ratio], color=color, edgecolor='black', height=0.5)
    ax.axvline(x=10, color='red', linestyle='--', linewidth=2, label='10% threshold')
    ax.axvline(x=0, color='black', linewidth=1)

    ax.set_xlabel('Improvement (%)', fontsize=12)
    ax.set_title('Sample Efficiency Improvement: fine_gated vs fine_always', fontsize=14, fontweight='bold')
    ax.set_xlim(-20, max(ratio + 20, 30))
    ax.legend(loc='upper right', fontsize=10)

    ax.text(ratio + 1, 0, f'{ratio:.1f}%', va='center', fontsize=12, fontweight='bold')

    status = "PASS" if ratio > 10 else "FAIL"
    ax.text(0.02, 0.95, f'Status: {status}', transform=ax.transAxes,
            fontsize=12, fontweight='bold', color='green' if ratio > 10 else 'red')

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


def generate_all_figures(results_path: str, figures_dir: str):
    """Generate all figures from experiment results."""
    os.makedirs(figures_dir, exist_ok=True)

    with open(results_path, 'r') as f:
        results = json.load(f)

    steps_always = results.get('fine_always', {}).get('steps_to_30pct')
    steps_gated = results.get('fine_gated', {}).get('steps_to_30pct')

    plot_gate_metrics_comparison(
        steps_gated=steps_gated,
        steps_always=steps_always,
        path=f"{figures_dir}/gate_metrics_comparison.png"
    )

    curves = {
        'fine_always': results.get('fine_always', {}).get('pass_at_1_curve', []),
        'fine_gated': results.get('fine_gated', {}).get('pass_at_1_curve', []),
    }
    plot_training_curves(curves, f"{figures_dir}/training_curves.png")

    gating_stats = results.get('fine_gated', {}).get('gating_stats', {})
    u_line = int(gating_stats.get('u_line_rate', 0) * gating_stats.get('total', 0))
    u_ignore = int(gating_stats.get('u_ignore_rate', 0) * gating_stats.get('total', 0))
    plot_error_distribution(u_line, u_ignore, f"{figures_dir}/error_distribution.png")

    plot_efficiency_ratio(steps_gated, steps_always, f"{figures_dir}/efficiency_ratio.png")

    print(f"\nAll figures generated in {figures_dir}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        results_path = sys.argv[1]
        figures_dir = sys.argv[2] if len(sys.argv) > 2 else "figures"
    else:
        results_path = "outputs/experiment_results.json"
        figures_dir = "../figures"

    generate_all_figures(results_path, figures_dir)
