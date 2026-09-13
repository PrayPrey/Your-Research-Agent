"""
Visualization Extension - Phase 1 specific plots
Task: A-5
Hypothesis: h-m1
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os


sns.set_style("whitegrid")


def plot_weight_trajectory(weight_trajectory, save_path="./figures/weight_trajectory.png"):
    """Plot weight trajectory with Phase 1 highlighting."""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    progress = [w['progress'] for w in weight_trajectory]
    exec_w = [w['execution_weight'] for w in weight_trajectory]
    ai_w = [w['ai_weight'] for w in weight_trajectory]
    human_w = [w['human_weight'] for w in weight_trajectory]

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(progress, exec_w, 'r-', label='Execution', linewidth=2)
    ax.plot(progress, ai_w, 'b-', label='AI', linewidth=2)
    ax.plot(progress, human_w, 'g-', label='Human', linewidth=2)

    # Highlight Phase 1 region
    ax.axvspan(0, 0.3, alpha=0.2, color='yellow', label='Phase 1 (0-30%)')
    ax.axvline(0.3, color='gray', linestyle='--', alpha=0.5)
    ax.axvline(0.7, color='gray', linestyle='--', alpha=0.5)

    ax.set_xlabel('Training Progress', fontsize=12)
    ax.set_ylabel('Weight Coefficient', fontsize=12)
    ax.set_title('Tri-Modal Weight Trajectory (Phase 1 Analysis)', fontsize=14)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

    print(f"✓ Saved: {save_path}")


def plot_pass_at_1_trajectory(pass_at_1_trajectory, save_path="./figures/pass_at_1_trajectory.png"):
    """Plot pass@1 trajectory with phase boundaries."""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    progress = [p['progress'] for p in pass_at_1_trajectory]
    pass_at_1 = [p['pass_at_1'] for p in pass_at_1_trajectory]

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(progress, pass_at_1, 'o-', color='purple', linewidth=2, markersize=8)

    # Phase boundaries
    ax.axvline(0.3, color='red', linestyle='--', label='Phase 1 End', alpha=0.7)
    ax.axvline(0.7, color='blue', linestyle='--', label='Phase 2 End', alpha=0.7)

    ax.set_xlabel('Training Progress', fontsize=12)
    ax.set_ylabel('Pass@1 Score', fontsize=12)
    ax.set_title('Pass@1 Improvement Across Training Phases', fontsize=14)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

    print(f"✓ Saved: {save_path}")


def plot_phase_improvement_rates(improvement_metrics, save_path="./figures/phase_improvement_rates.png"):
    """Plot improvement rates comparison (Phase 1 vs later)."""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    phases = ['Phase 1\n(0-30%)', 'Later\n(30-100%)']
    rates = [improvement_metrics['phase1_rate'], improvement_metrics['later_rate']]

    fig, ax = plt.subplots(figsize=(8, 6))

    bars = ax.bar(phases, rates, color=['#ff6b6b', '#4ecdc4'], alpha=0.8)
    ax.set_ylabel('Pass@1 Improvement Rate', fontsize=12)
    ax.set_title('Pass@1 Improvement Rates by Phase', fontsize=14)
    ax.grid(True, alpha=0.3, axis='y')

    # Add value labels on bars
    for bar, rate in zip(bars, rates):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{rate:.4f}', ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

    print(f"✓ Saved: {save_path}")


def plot_gate_metrics(gate_metrics, save_path="./figures/gate_metrics.png"):
    """Plot gate validation metrics (mandatory for 04_validation.md)."""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Metric 1: Weight Dominance
    ax = axes[0]
    checkpoints = gate_metrics['metric1_weight_dominance']['checkpoints']
    progress = [c['progress'] for c in checkpoints]
    exec_w = [c['execution_weight'] for c in checkpoints]
    max_other = [max(c['ai_weight'], c['human_weight']) for c in checkpoints]

    ax.plot(progress, exec_w, 'ro-', label='Execution Weight', linewidth=2, markersize=8)
    ax.plot(progress, max_other, 'bs-', label='Max(AI, Human)', linewidth=2, markersize=8)
    ax.set_xlabel('Training Progress', fontsize=10)
    ax.set_ylabel('Weight', fontsize=10)
    ax.set_title('Metric 1: Weight Dominance', fontsize=12)
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Metric 2: Improvement Rates
    ax = axes[1]
    improvement = gate_metrics['metric2_pass_at_1_improvement']
    rates = [improvement['phase1_rate'], improvement['later_rate']]
    ax.bar(['Phase 1', 'Later'], rates, color=['#ff6b6b', '#4ecdc4'], alpha=0.8)
    ax.set_ylabel('Improvement Rate', fontsize=10)
    ax.set_title('Metric 2: Pass@1 Improvement', fontsize=12)
    ax.grid(True, alpha=0.3, axis='y')

    # Metric 3: Correlation
    ax = axes[2]
    corr_data = gate_metrics['metric3_weight_correlation']
    ax.bar(['Correlation'], [corr_data['correlation']], color='green' if corr_data['passed'] else 'red', alpha=0.8)
    ax.axhline(y=-0.5, color='orange', linestyle='--', label='Threshold')
    ax.set_ylabel('Pearson ρ', fontsize=10)
    ax.set_title('Metric 3: Weight Correlation', fontsize=12)
    ax.set_ylim(-1, 1)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

    print(f"✓ Saved: {save_path}")
