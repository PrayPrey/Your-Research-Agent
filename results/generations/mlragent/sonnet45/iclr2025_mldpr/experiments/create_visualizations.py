"""
Visualization Module for Temporal Dataset Cards Experiments
Generate publication-quality figures
"""

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from typing import Dict, List
import json

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 11


def plot_reproducibility_comparison(results: Dict, output_path: str):
    """Plot reproducibility comparison between systems"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    with_tracking = results['experiment_1_reproducibility']['with_temporal_cards']
    without_tracking = results['experiment_1_reproducibility']['without_temporal_cards']

    # Plot 1: Result distributions
    ax = axes[0, 0]
    data_with = with_tracking['results']
    data_without = without_tracking['results']

    ax.hist(data_without, bins=20, alpha=0.6, label='Without Temporal Cards', color='coral')
    ax.hist(data_with, bins=20, alpha=0.6, label='With Temporal Cards', color='skyblue')
    ax.set_xlabel('Reported Accuracy')
    ax.set_ylabel('Frequency')
    ax.set_title('Distribution of Reproduced Results')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Plot 2: Variance comparison
    ax = axes[0, 1]
    categories = ['Without\nTemporal Cards', 'With\nTemporal Cards']
    variances = [without_tracking['variance'], with_tracking['variance']]
    colors = ['coral', 'skyblue']

    bars = ax.bar(categories, variances, color=colors, alpha=0.7)
    ax.set_ylabel('Variance')
    ax.set_title('Result Variance Comparison')
    ax.grid(True, alpha=0.3, axis='y')

    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.4f}',
                ha='center', va='bottom')

    # Plot 3: Success rate comparison
    ax = axes[1, 0]
    success_rates = [
        without_tracking['reproduction_success_rate'] * 100,
        with_tracking['reproduction_success_rate'] * 100
    ]

    bars = ax.bar(categories, success_rates, color=colors, alpha=0.7)
    ax.set_ylabel('Success Rate (%)')
    ax.set_title('Reproduction Success Rate')
    ax.set_ylim([0, 100])
    ax.grid(True, alpha=0.3, axis='y')

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom')

    # Plot 4: Improvement metrics
    ax = axes[1, 1]
    improvement = results['experiment_1_reproducibility']['improvement']
    metrics = ['Variance\nReduction', 'Success Rate\nImprovement', 'CV\nReduction']
    values = [
        improvement['variance_reduction_percent'],
        improvement['success_rate_improvement_percent'],
        improvement['cv_reduction_percent']
    ]

    bars = ax.bar(metrics, values, color='seagreen', alpha=0.7)
    ax.set_ylabel('Improvement (%)')
    ax.set_title('Overall Improvements with Temporal Cards')
    ax.grid(True, alpha=0.3, axis='y')
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom' if height > 0 else 'top')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")


def plot_impact_tracing_comparison(results: Dict, output_path: str):
    """Plot impact tracing accuracy comparison"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    automated = results['experiment_2_impact_tracing']['automated_tracing']
    manual = results['experiment_2_impact_tracing']['manual_review']

    # Plot 1: Precision, Recall, F1
    ax = axes[0]
    metrics = ['Precision', 'Recall', 'F1 Score']
    automated_values = [automated['precision'], automated['recall'], automated['f1_score']]
    manual_values = [manual['precision'], manual['recall'], manual['f1_score']]

    x = np.arange(len(metrics))
    width = 0.35

    bars1 = ax.bar(x - width/2, manual_values, width, label='Manual Review', color='coral', alpha=0.7)
    bars2 = ax.bar(x + width/2, automated_values, width, label='Automated Tracing', color='skyblue', alpha=0.7)

    ax.set_ylabel('Score')
    ax.set_title('Impact Tracing Performance Metrics')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.legend()
    ax.set_ylim([0, 1.0])
    ax.grid(True, alpha=0.3, axis='y')

    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.3f}',
                    ha='center', va='bottom', fontsize=9)

    # Plot 2: Confusion matrix style
    ax = axes[1]
    categories = ['True\nPositives', 'False\nPositives', 'False\nNegatives']
    automated_counts = [automated['true_positives'], automated['false_positives'], automated['false_negatives']]
    manual_counts = [manual['true_positives'], manual['false_positives'], manual['false_negatives']]

    x = np.arange(len(categories))
    bars1 = ax.bar(x - width/2, manual_counts, width, label='Manual Review', color='coral', alpha=0.7)
    bars2 = ax.bar(x + width/2, automated_counts, width, label='Automated Tracing', color='skyblue', alpha=0.7)

    ax.set_ylabel('Count')
    ax.set_title('Citation Detection Counts')
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")


def plot_annotation_propagation(results: Dict, output_path: str):
    """Plot annotation propagation effectiveness"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    with_system = results['experiment_3_annotation_propagation']['with_temporal_system']
    without_system = results['experiment_3_annotation_propagation']['without_temporal_system']

    # Plot 1: Propagation rate
    ax = axes[0, 0]
    categories = ['Manual\nPropagation', 'Temporal Card\nSystem']
    rates = [
        without_system['propagation_rate'] * 100,
        with_system['propagation_rate'] * 100
    ]
    colors = ['coral', 'skyblue']

    bars = ax.bar(categories, rates, color=colors, alpha=0.7)
    ax.set_ylabel('Propagation Rate (%)')
    ax.set_title('Annotation Propagation Rate')
    ax.set_ylim([0, 100])
    ax.grid(True, alpha=0.3, axis='y')

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom')

    # Plot 2: Notification time
    ax = axes[0, 1]
    times = [
        without_system['avg_notification_time_days'],
        with_system['avg_notification_time_days']
    ]

    bars = ax.bar(categories, times, color=colors, alpha=0.7)
    ax.set_ylabel('Average Time (days)')
    ax.set_title('Time to User Notification')
    ax.grid(True, alpha=0.3, axis='y')

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}d',
                ha='center', va='bottom')

    # Plot 3: User acknowledgment
    ax = axes[1, 0]
    ack_rates = [
        without_system['user_acknowledgment_rate'] * 100,
        with_system['user_acknowledgment_rate'] * 100
    ]

    bars = ax.bar(categories, ack_rates, color=colors, alpha=0.7)
    ax.set_ylabel('Acknowledgment Rate (%)')
    ax.set_title('User Acknowledgment Rate')
    ax.set_ylim([0, 100])
    ax.grid(True, alpha=0.3, axis='y')

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom')

    # Plot 4: Notification time distribution
    ax = axes[1, 1]
    times_with = with_system['notification_times']
    times_without = without_system['notification_times']

    ax.hist(times_without, bins=15, alpha=0.6, label='Manual Propagation', color='coral')
    ax.hist(times_with, bins=15, alpha=0.6, label='Temporal Card System', color='skyblue')
    ax.set_xlabel('Notification Time (days)')
    ax.set_ylabel('Frequency')
    ax.set_title('Distribution of Notification Times')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")


def plot_statistical_divergence(results: Dict, output_path: str):
    """Plot statistical divergence between versions"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    divergences = results['experiment_4_statistical_signatures']['divergences']
    result_variances = results['experiment_4_statistical_signatures']['result_variances']

    # Plot 1: KL Divergence between consecutive versions
    ax = axes[0]
    transitions = [f"{d['from_version']}\n→\n{d['to_version']}" for d in divergences]
    kl_divs = [d['kl_divergence'] for d in divergences]

    bars = ax.bar(range(len(transitions)), kl_divs, color='mediumpurple', alpha=0.7)
    ax.set_xlabel('Version Transition')
    ax.set_ylabel('KL Divergence')
    ax.set_title('Distribution Divergence Between Versions')
    ax.set_xticks(range(len(transitions)))
    ax.set_xticklabels(transitions, fontsize=9)
    ax.grid(True, alpha=0.3, axis='y')

    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.4f}',
                ha='center', va='bottom', fontsize=9)

    # Plot 2: Result variance by version
    ax = axes[1]
    versions = list(result_variances.keys())
    variances = [result_variances[v]['variance'] for v in versions]
    means = [result_variances[v]['mean'] for v in versions]

    x = range(len(versions))
    ax.bar(x, variances, color='seagreen', alpha=0.7, label='Variance')
    ax.set_xlabel('Dataset Version')
    ax.set_ylabel('Result Variance')
    ax.set_title('Performance Variance Across Versions')
    ax.set_xticks(x)
    ax.set_xticklabels(versions)
    ax.grid(True, alpha=0.3, axis='y')

    for i, (var, mean) in enumerate(zip(variances, means)):
        ax.text(i, var, f'{var:.5f}\n(μ={mean:.3f})',
                ha='center', va='bottom', fontsize=8)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")


def plot_summary_comparison(summary: Dict, output_path: str):
    """Create comprehensive summary comparison plot"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Plot 1: Reproducibility improvements
    ax = axes[0, 0]
    metrics = ['Variance\nReduction (%)', 'Success Rate\nImprovement (%)']
    values = [
        summary['reproducibility']['variance_reduction'],
        summary['reproducibility']['success_rate_improvement']
    ]
    colors = ['#2ecc71', '#3498db']

    bars = ax.bar(metrics, values, color=colors, alpha=0.7)
    ax.set_ylabel('Improvement (%)')
    ax.set_title('Reproducibility Improvements')
    ax.grid(True, alpha=0.3, axis='y')
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom', fontsize=10, fontweight='bold')

    # Plot 2: Impact tracing F1 scores
    ax = axes[0, 1]
    methods = ['Manual\nReview', 'Automated\nTracing']
    f1_scores = [
        summary['impact_tracing']['manual_f1'],
        summary['impact_tracing']['automated_f1']
    ]
    colors = ['coral', 'skyblue']

    bars = ax.bar(methods, f1_scores, color=colors, alpha=0.7)
    ax.set_ylabel('F1 Score')
    ax.set_title('Impact Tracing Performance')
    ax.set_ylim([0, 1.0])
    ax.grid(True, alpha=0.3, axis='y')

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.3f}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')

    # Plot 3: Annotation propagation comparison
    ax = axes[1, 0]
    systems = ['Manual', 'Temporal\nCard System']
    prop_rates = [
        summary['annotation_propagation']['manual_rate'] * 100,
        summary['annotation_propagation']['temporal_system_rate'] * 100
    ]

    bars = ax.bar(systems, prop_rates, color=colors, alpha=0.7)
    ax.set_ylabel('Propagation Rate (%)')
    ax.set_title('Annotation Propagation Effectiveness')
    ax.set_ylim([0, 100])
    ax.grid(True, alpha=0.3, axis='y')

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom', fontsize=10, fontweight='bold')

    # Plot 4: Overall benefits radar chart style
    ax = axes[1, 1]
    metrics_summary = [
        'Reproducibility',
        'Impact Tracing',
        'Annotation\nPropagation',
        'Version\nTracking'
    ]

    # Normalize scores to 0-100 scale
    scores = [
        min(summary['reproducibility']['variance_reduction'], 100),
        summary['impact_tracing']['automated_f1'] * 100,
        summary['annotation_propagation']['temporal_system_rate'] * 100,
        100  # Version tracking always 100% with temporal cards
    ]

    bars = ax.barh(metrics_summary, scores, color='mediumseagreen', alpha=0.7)
    ax.set_xlabel('Effectiveness Score')
    ax.set_title('Overall System Effectiveness')
    ax.set_xlim([0, 100])
    ax.grid(True, alpha=0.3, axis='x')

    for i, (bar, score) in enumerate(zip(bars, scores)):
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2.,
                f' {score:.1f}',
                ha='left', va='center', fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")


def generate_all_visualizations(results: Dict, summary: Dict, output_dir: str):
    """Generate all visualization figures"""
    print("\nGenerating visualizations...")

    plot_reproducibility_comparison(results, f"{output_dir}/reproducibility_comparison.png")
    plot_impact_tracing_comparison(results, f"{output_dir}/impact_tracing_comparison.png")
    plot_annotation_propagation(results, f"{output_dir}/annotation_propagation.png")
    plot_statistical_divergence(results, f"{output_dir}/statistical_divergence.png")
    plot_summary_comparison(summary, f"{output_dir}/summary_comparison.png")

    print("\nAll visualizations generated successfully!")
