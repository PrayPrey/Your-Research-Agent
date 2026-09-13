#!/usr/bin/env python3
"""
LLM-Generated Figure Script for Phase 6 Paper
Generated based on actual h-m1 experiment results data.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
import numpy as np
from pathlib import Path

# Paths
FIGURES_DIR = Path("/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet45/TEST_data_problems/docs/youra_research/paper/figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

DATA_PATH = Path("/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet45/TEST_data_problems/docs/youra_research/h-m1/code/outputs/experiment_results.json")

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def create_mechanism_validation_chart(data):
    """
    Bar chart showing entropy and Fisher information across curation conditions.
    Figure supports h-m1 mechanism hypothesis validation.
    """
    conditions = [c['condition'] for c in data['conditions']]
    entropy_vals = [c['entropy'] for c in data['conditions']]
    fisher_vals = [c['fisher_trace'] for c in data['conditions']]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    # Entropy plot
    ax1.bar(conditions, entropy_vals, color=['#1f77b4', '#ff7f0e', '#2ca02c'], alpha=0.8)
    ax1.set_ylabel('Entropy (bits/token)', fontsize=11)
    ax1.set_xlabel('Curation Condition', fontsize=11)
    ax1.set_title('Information Density: Entropy', fontsize=12, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)

    # Fisher trace plot
    ax2.bar(conditions, fisher_vals, color=['#1f77b4', '#ff7f0e', '#2ca02c'], alpha=0.8)
    ax2.set_ylabel('Fisher Information (trace)', fontsize=11)
    ax2.set_xlabel('Curation Condition', fontsize=11)
    ax2.set_title('Gradient Signal: Fisher Trace', fontsize=12, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    output_path = FIGURES_DIR / "fig_mechanism_validation.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Generated: {output_path}")

def create_quality_comparison_chart(data):
    """
    Grouped bar chart comparing baseline vs full curation on entropy and Fisher.
    Normalizes to baseline for clarity.
    """
    baseline = data['conditions'][0]
    full = data['conditions'][2]

    # Normalize to baseline (percent change)
    entropy_change = ((full['entropy'] - baseline['entropy']) / baseline['entropy']) * 100
    fisher_change = ((full['fisher_trace'] - baseline['fisher_trace']) / baseline['fisher_trace']) * 100

    metrics = ['Entropy\nReduction (%)', 'Fisher\nIncrease (%)']
    values = [entropy_change, fisher_change]
    colors = ['#2ca02c' if v > 0 else '#d62728' for v in values]

    fig, ax = plt.subplots(figsize=(6, 5))
    bars = ax.bar(metrics, values, color=colors, alpha=0.8, edgecolor='black', linewidth=1.2)

    # Add threshold lines
    ax.axhline(y=-20, color='red', linestyle='--', linewidth=1.5, alpha=0.7, label='Gate Threshold (20%)')
    ax.axhline(y=15, color='green', linestyle='--', linewidth=1.5, alpha=0.7)

    ax.set_ylabel('Percent Change from Baseline (%)', fontsize=11)
    ax.set_title('Data Curation Effect on Information Metrics', fontsize=12, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    ax.legend(fontsize=9)

    # Add value labels on bars
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.1f}%', ha='center', va='bottom' if val > 0 else 'top', fontsize=10, fontweight='bold')

    plt.tight_layout()
    output_path = FIGURES_DIR / "fig_quality_comparison.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Generated: {output_path}")

def main():
    """Generate all figures from h-m1 experiment data."""
    data = load_json(DATA_PATH)

    print(f"Loaded data: {len(data['conditions'])} conditions")
    print(f"Gate result: {data['gate_result']}")
    print(f"PoC mode: {data['poc_mode']}")

    create_mechanism_validation_chart(data)
    create_quality_comparison_chart(data)

    print(f"\n✅ Generated 2 figures in {FIGURES_DIR}")

if __name__ == '__main__':
    main()
