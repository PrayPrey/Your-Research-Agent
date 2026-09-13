#!/usr/bin/env python3
"""
Phase 6 Figure Generation for Paper
Based on mechanism validation results from h-m-integrated
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
import numpy as np
from pathlib import Path

# Paths
FIGURES_DIR = Path("/home/anonymous/YouRA_results_new_4_sonnet45/TEST_scsl/docs/youra_research/20260318_scsl/paper/figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

DATA_FILE = Path("/home/anonymous/YouRA_results_new_4_sonnet45/TEST_scsl/docs/youra_research/20260318_scsl/h-m-integrated/results/mechanism_metrics.json")

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def create_mechanism_gates_chart(data):
    """Create bar chart showing mechanism gate results vs thresholds"""
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))

    # M1: AMI Score
    ax1 = axes[0]
    ami_value = data['m1']['ami_score']
    ami_threshold = 0.4

    bars1 = ax1.bar(['Observed\nAMI', 'Required\nThreshold'],
                    [ami_value, ami_threshold],
                    color=['#d62728' if ami_value < ami_threshold else '#2ca02c', '#808080'])
    ax1.axhline(y=ami_threshold, color='gray', linestyle='--', linewidth=1, alpha=0.7)
    ax1.set_ylabel('AMI Score', fontsize=11)
    ax1.set_title('M1: Cluster Formation\n(FAIL)', fontsize=12, fontweight='bold')
    ax1.set_ylim(0, 0.5)

    # Add value labels
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.3f}', ha='center', va='bottom', fontsize=10)

    # M2: Correlation (showing absolute value for visualization)
    ax2 = axes[1]
    corr_value = abs(data['m2']['correlation'])

    bars2 = ax2.bar(['Observed\n|Correlation|', 'Expected\n(Positive)'],
                    [corr_value, 0.5],
                    color=['#d62728', '#808080'])
    ax2.set_ylabel('|Correlation|', fontsize=11)
    ax2.set_title('M2: AMI-Efficacy Link\n(FAIL)', fontsize=12, fontweight='bold')
    ax2.set_ylim(0, 1.2)
    ax2.text(0, corr_value + 0.05, 'Negative\ncorrelation', ha='center', fontsize=9)

    # Add value labels
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}', ha='center', va='bottom', fontsize=10)

    # M3: AMI Reduction
    ax3 = axes[2]
    ami_reduction = data['m3']['ami_reduction'] * 100  # Convert to percentage
    threshold_reduction = -30  # Required reduction

    bars3 = ax3.bar(['Observed\nΔAMI', 'Required\nReduction'],
                    [ami_reduction, threshold_reduction],
                    color=['#d62728' if ami_reduction > threshold_reduction else '#2ca02c', '#808080'])
    ax3.axhline(y=threshold_reduction, color='gray', linestyle='--', linewidth=1, alpha=0.7)
    ax3.axhline(y=0, color='black', linewidth=0.8)
    ax3.set_ylabel('AMI Change (%)', fontsize=11)
    ax3.set_title('M3: Cluster Dispersion\n(FAIL)', fontsize=12, fontweight='bold')
    ax3.set_ylim(-35, 5)

    # Add value labels
    for bar in bars3:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%', ha='center', va='bottom' if height > 0 else 'top', fontsize=10)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "mechanism_gates_results.png", dpi=300, bbox_inches='tight')
    print(f"✓ Generated: mechanism_gates_results.png")
    plt.close()

def create_ami_comparison_chart(data):
    """Create comparison of SimCLR vs LA-SSL AMI scores"""
    fig, ax = plt.subplots(figsize=(6, 4))

    simclr_ami = data['m3']['ami_simclr']
    lassl_ami = data['m3']['ami_lassl']
    threshold = 0.4

    x = np.arange(2)
    bars = ax.bar(x, [simclr_ami, lassl_ami],
                   color=['#1f77b4', '#ff7f0e'],
                   width=0.6)

    # Threshold line
    ax.axhline(y=threshold, color='red', linestyle='--', linewidth=2,
               label=f'Required Threshold (AMI ≥ {threshold})')

    ax.set_ylabel('AMI Score', fontsize=12)
    ax.set_title('Embedding Clusterability: SimCLR vs LA-SSL', fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(['SimCLR\n(Standard SSL)', 'LA-SSL\n(Resampling)'], fontsize=11)
    ax.set_ylim(0, 0.5)
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(axis='y', alpha=0.3)

    # Add value labels
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.3f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "ami_comparison.png", dpi=300, bbox_inches='tight')
    print(f"✓ Generated: ami_comparison.png")
    plt.close()

def main():
    # Load mechanism metrics
    data = load_json(DATA_FILE)

    print("Generating figures from mechanism validation results...")

    # Create figures
    create_mechanism_gates_chart(data)
    create_ami_comparison_chart(data)

    print(f"\n✓ All figures generated in {FIGURES_DIR}")
    print(f"  Total: 2 figures")

if __name__ == '__main__':
    main()
