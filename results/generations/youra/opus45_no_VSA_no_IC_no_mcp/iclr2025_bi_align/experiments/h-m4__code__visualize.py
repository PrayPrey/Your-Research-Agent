"""Visualization for H-M4 profile comparison."""
import numpy as np
import matplotlib.pyplot as plt
from typing import List


def plot_profile_comparison(dpo_profile: List[float], rlhf_profile: List[float],
                             benchmarks: List[str], out_path: str) -> None:
    """Generate radar chart comparing DPO vs RLHF profiles."""
    # Setup radar chart
    angles = np.linspace(0, 2 * np.pi, len(benchmarks), endpoint=False).tolist()
    angles += angles[:1]

    dpo_values = dpo_profile + [dpo_profile[0]]
    rlhf_values = rlhf_profile + [rlhf_profile[0]]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

    ax.plot(angles, dpo_values, 'o-', linewidth=2, label='DPO', color='#2196F3')
    ax.fill(angles, dpo_values, alpha=0.25, color='#2196F3')

    ax.plot(angles, rlhf_values, 's-', linewidth=2, label='RLHF', color='#F44336')
    ax.fill(angles, rlhf_values, alpha=0.25, color='#F44336')

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([b.replace('_', '\n') for b in benchmarks], size=10)

    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8])
    ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8'], size=8)

    ax.legend(loc='upper right', bbox_to_anchor=(1.15, 1.1))
    ax.set_title('H-M4: Differential Benchmark Profiles\nDPO vs RLHF', size=14, pad=20)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_effect_sizes(effects: dict, out_path: str) -> None:
    """Bar chart of Cohen's d per benchmark."""
    benchmarks = list(effects.keys())
    d_values = [effects[b]["cohens_d"] for b in benchmarks]

    fig, ax = plt.subplots(figsize=(10, 6))

    colors = ['#4CAF50' if abs(d) > 0.3 else '#FFC107' if abs(d) > 0.15 else '#9E9E9E' for d in d_values]
    bars = ax.bar(benchmarks, d_values, color=colors, edgecolor='black')

    ax.axhline(y=0.3, color='green', linestyle='--', label='Large effect (|d|>0.3)')
    ax.axhline(y=-0.3, color='green', linestyle='--')
    ax.axhline(y=0.15, color='orange', linestyle='--', label='Small effect (|d|=0.15)')
    ax.axhline(y=-0.15, color='orange', linestyle='--')
    ax.axhline(y=0, color='black', linewidth=0.5)

    ax.set_ylabel("Cohen's d (DPO - RLHF)", size=12)
    ax.set_xlabel("Benchmark", size=12)
    ax.set_title("H-M4: Effect Sizes by Benchmark", size=14)
    ax.legend(loc='upper right')

    for bar, d in zip(bars, d_values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{d:.3f}', ha='center', va='bottom', size=10)

    plt.tight_layout()
    plt.savefig(out_path.replace('.png', '_effects.png'), dpi=150)
    plt.close()
