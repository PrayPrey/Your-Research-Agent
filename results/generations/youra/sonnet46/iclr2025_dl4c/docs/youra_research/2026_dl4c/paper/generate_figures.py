#!/usr/bin/env python3
"""
LLM-Generated Figure Script for Phase 6 Paper
Research: Prescreening-Gated R_ratio vs R_binary for GRPO
Generated based on actual data structure and research context.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

FIGURES_DIR = Path(__file__).parent / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

def create_binomial_variance_comparison():
    """
    Figure 1: Analytical comparison of E[Var(r_ratio)] vs E[Var(r_binary)]
    as a function of problem tractability q.
    This is the core theoretical claim of the paper.
    Data: Derived analytically from Binomial(T,q) model.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    q = np.linspace(0.01, 0.99, 500)
    T_values = [3, 5, 8, 10]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

    # Left: Variance curves for different T
    for T, color in zip(T_values, colors):
        var_ratio = q * (1 - q)           # E[Var(r_ratio)] = q(1-q)
        var_binary = q**T * (1 - q**T)    # E[Var(r_binary)]
        ax1.plot(q, var_ratio, color=color, linestyle='-', linewidth=2, label=f'R_ratio (T={T})', alpha=0.9)
        ax1.plot(q, var_binary, color=color, linestyle='--', linewidth=1.5, label=f'R_binary (T={T})', alpha=0.7)

    ax1.axvspan(0.3, 0.55, alpha=0.15, color='green', label='Target window [0.3, 0.55]')
    ax1.set_xlabel('Problem Tractability q', fontsize=11)
    ax1.set_ylabel('Expected Within-Group Variance', fontsize=11)
    ax1.set_title('E[Var(r_ratio)] vs E[Var(r_binary)]', fontsize=12)
    ax1.legend(fontsize=7, ncol=2)
    ax1.grid(True, alpha=0.3)

    # Right: Variance ratio E[Var(r_ratio)] / E[Var(r_binary)] for T in {3,5,8,10}
    for T, color in zip(T_values, colors):
        var_ratio = q * (1 - q)
        var_binary = q**T * (1 - q**T)
        ratio = np.where(var_binary > 1e-10, var_ratio / var_binary, np.nan)
        ax2.plot(q, ratio, color=color, linewidth=2, label=f'T={T}')

    ax2.axhline(y=1.5, color='red', linestyle=':', linewidth=1.5, label='1.5× threshold')
    ax2.axvspan(0.3, 0.55, alpha=0.15, color='green', label='Target window')
    ax2.set_xlabel('Problem Tractability q', fontsize=11)
    ax2.set_ylabel('Variance Ratio (R_ratio / R_binary)', fontsize=11)
    ax2.set_title('Variance Advantage of R_ratio over R_binary', fontsize=12)
    ax2.set_ylim(0, 25)
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    path = FIGURES_DIR / "fig_variance_advantage.png"
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


def create_prescreening_pipeline():
    """
    Figure 2: Prescreening pipeline architecture diagram.
    """
    fig, ax = plt.subplots(figsize=(10, 3.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis('off')

    boxes = [
        (0.5, 1.5, 1.5, 1.0, 'APPS\nDataset\n(1,923 probs)', '#AED6F1'),
        (2.5, 1.5, 1.5, 1.0, 'Model Inference\nk=8 rollouts\nT=0.8', '#A9DFBF'),
        (4.5, 1.5, 1.5, 1.0, 'S_term\nComputation\nr=tests_pass/T', '#FAD7A0'),
        (6.5, 1.5, 1.5, 1.0, 'Prescreening\nFilter\nS∈[0.3,0.55]', '#F1948A'),
        (8.5, 1.5, 1.5, 1.0, 'Variance\nRatio Gate\n≥1.5× ≥80%', '#D2B4DE'),
    ]

    for (x, y, w, h, label, color) in boxes:
        rect = mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                                        facecolor=color, edgecolor='gray', linewidth=1.5)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, label, ha='center', va='center', fontsize=8.5,
                fontweight='bold', wrap=True)

    # Arrows
    for i in range(4):
        x_start = boxes[i][0] + boxes[i][2]
        x_end = boxes[i+1][0]
        y_mid = 2.0
        ax.annotate('', xy=(x_end, y_mid), xytext=(x_start, y_mid),
                    arrowprops=dict(arrowstyle='->', lw=1.5, color='#2C3E50'))

    # Labels under boxes
    labels_bottom = ['Load', 'Execute', 'Compute', 'Filter', 'Gate']
    for i, (x, y, w, h, _, _) in enumerate(boxes):
        ax.text(x + w/2, y - 0.3, labels_bottom[i], ha='center', fontsize=7.5, color='gray')

    ax.set_title('Prescreening Pipeline Architecture (h-e1)', fontsize=13, fontweight='bold', pad=10)

    path = FIGURES_DIR / "fig_prescreening_pipeline.png"
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


def create_grpo_gradient_theory():
    """
    Figure 3: Theoretical illustration of GRPO gradient advantage distribution
    under R_ratio vs R_binary for a group of G=8 rollouts.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    np.random.seed(42)

    # Simulate advantage distributions for G=8 within a group
    # R_binary: near-binary {-1, +1} advantages
    # R_ratio: graded continuous advantages
    q = 0.45  # example tractability
    T = 5

    n_groups = 500
    binary_advantages = []
    ratio_advantages = []

    for _ in range(n_groups):
        # Simulate k=8 rollouts
        k = 8
        # Each rollout: pass T tests with probability q independently
        tests_passed = np.random.binomial(T, q, k)
        r_ratio = tests_passed / T
        r_binary = (tests_passed == T).astype(float)

        # GRPO: normalize within group
        if r_ratio.std() > 1e-8:
            adv_ratio = (r_ratio - r_ratio.mean()) / r_ratio.std()
        else:
            adv_ratio = np.zeros(k)

        if r_binary.std() > 1e-8:
            adv_binary = (r_binary - r_binary.mean()) / r_binary.std()
        else:
            adv_binary = np.zeros(k)

        ratio_advantages.extend(adv_ratio.tolist())
        binary_advantages.extend(adv_binary.tolist())

    ax1.hist(ratio_advantages, bins=40, color='#2196F3', alpha=0.7, edgecolor='white', linewidth=0.5)
    ax1.set_xlabel('Normalized Advantage A_i', fontsize=11)
    ax1.set_ylabel('Frequency', fontsize=11)
    ax1.set_title('R_ratio: Graded Advantage Distribution\n(q=0.45, T=5, G=8)', fontsize=11)
    ax1.grid(True, alpha=0.3)

    ax2.hist(binary_advantages, bins=20, color='#F44336', alpha=0.7, edgecolor='white', linewidth=0.5)
    ax2.set_xlabel('Normalized Advantage A_i', fontsize=11)
    ax2.set_ylabel('Frequency', fontsize=11)
    ax2.set_title('R_binary: Near-Binary Advantage Distribution\n(q=0.45, T=5, G=8)', fontsize=11)
    ax2.grid(True, alpha=0.3)

    # Count distinct levels
    ratio_distinct = len(set(np.round(ratio_advantages, 2)))
    binary_distinct = len(set(np.round(binary_advantages, 2)))
    ax1.text(0.05, 0.93, f'Distinct levels ≈ {ratio_distinct}', transform=ax1.transAxes,
             fontsize=9, color='#1565C0', fontweight='bold')
    ax2.text(0.05, 0.93, f'Distinct levels ≈ {binary_distinct}', transform=ax2.transAxes,
             fontsize=9, color='#B71C1C', fontweight='bold')

    plt.tight_layout()
    path = FIGURES_DIR / "fig_advantage_distribution.png"
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


def create_prescreening_result_summary():
    """
    Figure 4: Summary of h-e1 experiment results.
    Shows metric values vs thresholds for the PARTIAL gate evaluation.
    """
    fig, ax = plt.subplots(figsize=(8, 4))

    metrics = ['fraction_k_pass_ge1\n(threshold ≥0.10)', 'pct_groups_above_1.5x\n(threshold ≥0.80)',
               'n_prescreened\n(threshold ≥50)']
    actual = [0.0, 0.0, 0]
    thresholds = [0.10, 0.80, 50]

    # Normalize for visualization
    thresh_norm = [1.0, 1.0, 1.0]
    actual_norm = [0.0, 0.0, 0.0]

    x = np.arange(len(metrics))
    width = 0.35

    bars_thresh = ax.bar(x - width/2, thresh_norm, width, label='Threshold (required)', color='#4CAF50', alpha=0.8)
    bars_actual = ax.bar(x + width/2, actual_norm, width, label='Actual (base model)', color='#F44336', alpha=0.8)

    # Threshold labels
    for i, (thresh, bar) in enumerate(zip(thresholds, bars_thresh)):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.02,
                f'{thresh}', ha='center', va='bottom', fontsize=9, fontweight='bold', color='#2E7D32')

    # Actual labels
    for i, (val, bar) in enumerate(zip(actual, bars_actual)):
        ax.text(bar.get_x() + bar.get_width()/2., 0.02,
                f'{val}', ha='center', va='bottom', fontsize=9, fontweight='bold', color='#B71C1C')

    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=9)
    ax.set_ylabel('Normalized Value (1.0 = threshold)', fontsize=10)
    ax.set_title('h-e1 Gate Metrics: Actual vs Threshold\n(PARTIAL result — base model, no SFT)', fontsize=11)
    ax.legend(fontsize=10)
    ax.set_ylim(0, 1.3)
    ax.text(0.5, 0.60, 'Base model: 0% pass rate → All metrics = 0\nInfrastructure verified: 15/15 tasks, 67/67 tests ✓',
            transform=ax.transAxes, ha='center', fontsize=10,
            bbox=dict(boxstyle='round', facecolor='#FFF9C4', alpha=0.8))
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    path = FIGURES_DIR / "fig_gate_metrics.png"
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


def main():
    print("Generating figures for Phase 6 paper...")
    create_binomial_variance_comparison()
    create_prescreening_pipeline()
    create_grpo_gradient_theory()
    create_prescreening_result_summary()
    print(f"\nAll figures saved to: {FIGURES_DIR}")
    import os
    figs = list(FIGURES_DIR.glob("*.png"))
    print(f"Total figures: {len(figs)}")
    for f in sorted(figs):
        print(f"  - {f.name}")

if __name__ == '__main__':
    main()
