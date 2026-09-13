#!/usr/bin/env python3
"""
LLM-Generated Figure Script for Phase 6 Paper
Generated based on actual data structure and research context.

Research Context: Documentation Copilot System for ML Datasets
- Hypothesis: AI-assisted documentation copilot achieves >=70% acceptance rate
- Results: 92% median acceptance rate (significantly exceeded target)
- Data: 1,875 suggestions from 75 pilot users across vision/NLP/tabular datasets
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
import numpy as np
from pathlib import Path
from collections import Counter

# Paths
RESULTS_JSON = Path("/home/anonymous/YouRA_results_new_4_sonnet45_no_mcp/TEST_mldpr/docs/youra_research/20260415_mldpr/h-e1/code/outputs/results.json")
SUGGESTIONS_JSON = Path("/home/anonymous/YouRA_results_new_4_sonnet45_no_mcp/TEST_mldpr/docs/youra_research/20260415_mldpr/h-e1/code/data/logs/suggestions_log.json")
INTERACTIONS_JSON = Path("/home/anonymous/YouRA_results_new_4_sonnet45_no_mcp/TEST_mldpr/docs/youra_research/20260415_mldpr/h-e1/code/data/logs/user_interactions.json")
FIGURES_DIR = Path("/home/anonymous/YouRA_results_new_4_sonnet45_no_mcp/TEST_mldpr/docs/youra_research/20260415_mldpr/paper/figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Matplotlib style
plt.rcParams['figure.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['legend.fontsize'] = 9

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def create_acceptance_rate_comparison(results_data):
    """
    Figure 1: Acceptance Rate - Target vs Actual
    Shows the primary result: 92% median acceptance rate vs 70% target
    """
    fig, ax = plt.subplots(figsize=(6, 4))

    categories = ['Target\n(Success\nThreshold)', 'Actual\nMedian', 'Actual\nOverall']
    values = [
        results_data['target_acceptance_rate'],
        results_data['median_acceptance_rate'],
        results_data['overall_acceptance_rate']
    ]
    colors = ['#d62728', '#2ca02c', '#1f77b4']

    bars = ax.bar(categories, values, color=colors, alpha=0.8, edgecolor='black', linewidth=1.2)

    # Add value labels on bars
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1.5,
                f'{val:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=11)

    # Add threshold line
    ax.axhline(y=70, color='red', linestyle='--', linewidth=1.5, label='Success Threshold (70%)')

    ax.set_ylabel('Acceptance Rate (%)', fontweight='bold')
    ax.set_title('Documentation Copilot: Acceptance Rate Results', fontweight='bold', pad=15)
    ax.set_ylim(0, 105)
    ax.legend(loc='upper left')
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'acceptance_rate_comparison.png', bbox_inches='tight')
    plt.close()
    print("✓ Generated: acceptance_rate_comparison.png")

def create_stratified_acceptance(results_data):
    """
    Figure 2: Acceptance Rate by Dataset Type
    Shows consistent performance across vision, NLP, and tabular datasets
    """
    fig, ax = plt.subplots(figsize=(7, 4))

    dataset_types = ['Vision', 'NLP', 'Tabular']
    rates = [
        results_data['stratified_rates']['vision'],
        results_data['stratified_rates']['nlp'],
        results_data['stratified_rates']['tabular']
    ]

    bars = ax.bar(dataset_types, rates, color=['#ff7f0e', '#9467bd', '#8c564b'],
                   alpha=0.8, edgecolor='black', linewidth=1.2)

    # Add value labels
    for bar, val in zip(bars, rates):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.8,
                f'{val:.1f}%', ha='center', va='bottom', fontweight='bold')

    # Add threshold line
    ax.axhline(y=70, color='red', linestyle='--', linewidth=1.5, label='Target (70%)')

    ax.set_ylabel('Acceptance Rate (%)', fontweight='bold')
    ax.set_xlabel('Dataset Type', fontweight='bold')
    ax.set_title('Acceptance Rate by Dataset Type', fontweight='bold', pad=15)
    ax.set_ylim(0, 100)
    ax.legend()
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'stratified_acceptance.png', bbox_inches='tight')
    plt.close()
    print("✓ Generated: stratified_acceptance.png")

def create_action_breakdown(interactions_data):
    """
    Figure 3: User Action Distribution
    Breakdown of accepted, modified, and rejected suggestions
    """
    actions = [interaction['action'] for interaction in interactions_data]
    action_counts = Counter(actions)

    # Calculate percentages
    total = sum(action_counts.values())
    action_labels = []
    action_sizes = []
    colors_map = {'accepted': '#2ca02c', 'modified': '#ff7f0e', 'rejected': '#d62728'}
    colors = []

    for action in ['accepted', 'modified', 'rejected']:
        count = action_counts.get(action, 0)
        pct = (count / total) * 100
        action_labels.append(f'{action.capitalize()}\n({count}, {pct:.1f}%)')
        action_sizes.append(count)
        colors.append(colors_map[action])

    fig, ax = plt.subplots(figsize=(7, 5))
    wedges, texts, autotexts = ax.pie(action_sizes, labels=action_labels, colors=colors,
                                        autopct='%1.1f%%', startangle=90,
                                        wedgeprops={'edgecolor': 'black', 'linewidth': 1.5},
                                        textprops={'fontsize': 10, 'fontweight': 'bold'})

    ax.set_title('User Action Distribution (N=1,875 suggestions)', fontweight='bold', pad=20, fontsize=12)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'action_breakdown.png', bbox_inches='tight')
    plt.close()
    print("✓ Generated: action_breakdown.png")

def create_dataset_type_distribution(suggestions_data):
    """
    Figure 4: Dataset Type Distribution in Pilot
    Shows the diversity of datasets in the pilot study
    """
    dataset_types = [s['dataset_type'] for s in suggestions_data]
    type_counts = Counter(dataset_types)

    fig, ax = plt.subplots(figsize=(7, 4))

    types = list(type_counts.keys())
    counts = list(type_counts.values())
    colors = ['#ff7f0e', '#9467bd', '#8c564b']

    bars = ax.bar(types, counts, color=colors, alpha=0.8, edgecolor='black', linewidth=1.2)

    # Add value labels
    for bar, val in zip(bars, counts):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 10,
                f'{val}', ha='center', va='bottom', fontweight='bold')

    ax.set_ylabel('Number of Suggestions', fontweight='bold')
    ax.set_xlabel('Dataset Type', fontweight='bold')
    ax.set_title('Dataset Type Distribution in Pilot Study', fontweight='bold', pad=15)
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'dataset_type_distribution.png', bbox_inches='tight')
    plt.close()
    print("✓ Generated: dataset_type_distribution.png")

def create_section_distribution(suggestions_data):
    """
    Figure 5: Suggestions by Documentation Section
    Shows which sections received the most copilot assistance
    """
    sections = [s['section_name'] for s in suggestions_data]
    section_counts = Counter(sections)

    # Sort by count
    sorted_sections = sorted(section_counts.items(), key=lambda x: x[1], reverse=True)
    section_names = [s[0] for s in sorted_sections]
    counts = [s[1] for s in sorted_sections]

    fig, ax = plt.subplots(figsize=(8, 5))

    bars = ax.barh(section_names, counts, color='#1f77b4', alpha=0.8, edgecolor='black', linewidth=1.2)

    # Add value labels
    for bar, val in zip(bars, counts):
        width = bar.get_width()
        ax.text(width + 10, bar.get_y() + bar.get_height()/2.,
                f'{val}', ha='left', va='center', fontweight='bold')

    ax.set_xlabel('Number of Suggestions', fontweight='bold')
    ax.set_title('Suggestions by Documentation Section', fontweight='bold', pad=15)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    ax.invert_yaxis()  # Highest at top

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'section_distribution.png', bbox_inches='tight')
    plt.close()
    print("✓ Generated: section_distribution.png")

def main():
    print("Starting figure generation for Phase 6 Paper...")
    print(f"Output directory: {FIGURES_DIR}")

    # Load data
    print("\nLoading data files...")
    results_data = load_json(RESULTS_JSON)
    suggestions_data = load_json(SUGGESTIONS_JSON)
    interactions_data = load_json(INTERACTIONS_JSON)

    print(f"✓ Loaded results: {results_data['hypothesis_id']}")
    print(f"✓ Loaded {len(suggestions_data)} suggestions")
    print(f"✓ Loaded {len(interactions_data)} interactions")

    # Generate figures
    print("\nGenerating figures...")
    create_acceptance_rate_comparison(results_data)
    create_stratified_acceptance(results_data)
    create_action_breakdown(interactions_data)
    create_dataset_type_distribution(suggestions_data)
    create_section_distribution(suggestions_data)

    print(f"\n✅ All figures generated successfully in {FIGURES_DIR}")
    print(f"\nGenerated files:")
    for fig_file in sorted(FIGURES_DIR.glob("*.png")):
        print(f"  - {fig_file.name}")

if __name__ == '__main__':
    main()
