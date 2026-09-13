"""Visualization module for SpecBridge experiment results."""

import os
import json
import matplotlib.pyplot as plt
import numpy as np

def load_results(results_file):
    """Load experiment results from JSON file."""
    with open(results_file, 'r') as f:
        return json.load(f)

def plot_success_rate_comparison(metrics, output_dir):
    """Plot success rate comparison across methods."""
    methods = ['baseline', 'specbridge_static', 'specbridge_dynamic']
    method_names = ['Baseline\n(Direct LLM)', 'SpecBridge\nStatic', 'SpecBridge\nDynamic']
    success_rates = [metrics[m]['success_rate'] * 100 for m in methods]

    fig, ax = plt.subplots(figsize=(8, 6))

    colors = ['#3498db', '#2ecc71', '#9b59b6']
    bars = ax.bar(method_names, success_rates, color=colors, edgecolor='black', linewidth=1.5)

    # Add value labels on bars
    for bar, rate in zip(bars, success_rates):
        height = bar.get_height()
        ax.annotate(f'{rate:.1f}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=12, fontweight='bold')

    ax.set_ylabel('Success Rate (%)', fontsize=12)
    ax.set_title('Code Generation Verification Success Rate', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'success_rate_comparison.png'), dpi=150, bbox_inches='tight')
    plt.close()

def plot_pass_rate_distribution(results, output_dir):
    """Plot pass rate distribution for each method."""
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))

    methods = ['baseline', 'specbridge_static', 'specbridge_dynamic']
    titles = ['Baseline (Direct LLM)', 'SpecBridge Static', 'SpecBridge Dynamic']
    colors = ['#3498db', '#2ecc71', '#9b59b6']

    for ax, method, title, color in zip(axes, methods, titles, colors):
        pass_rates = [r['pass_rate'] * 100 for r in results[method]]

        ax.hist(pass_rates, bins=10, range=(0, 100), color=color, alpha=0.7, edgecolor='black')
        ax.axvline(np.mean(pass_rates), color='red', linestyle='--', linewidth=2, label=f'Mean: {np.mean(pass_rates):.1f}%')
        ax.set_xlabel('Pass Rate (%)', fontsize=10)
        ax.set_ylabel('Number of Problems', fontsize=10)
        ax.set_title(title, fontsize=11, fontweight='bold')
        ax.legend()
        ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'pass_rate_distribution.png'), dpi=150, bbox_inches='tight')
    plt.close()

def plot_difficulty_breakdown(metrics, output_dir):
    """Plot success rate by problem difficulty."""
    methods = ['baseline', 'specbridge_static', 'specbridge_dynamic']
    method_names = ['Baseline', 'SpecBridge Static', 'SpecBridge Dynamic']
    difficulties = ['easy', 'medium', 'hard']

    # Prepare data
    data = {m: [] for m in method_names}
    for method, name in zip(methods, method_names):
        for diff in difficulties:
            if diff in metrics[method].get('by_difficulty', {}):
                data[name].append(metrics[method]['by_difficulty'][diff]['success_rate'] * 100)
            else:
                data[name].append(0)

    # Filter out difficulties with no data
    valid_difficulties = []
    for i, diff in enumerate(difficulties):
        if any(data[name][i] > 0 or metrics[methods[0]].get('by_difficulty', {}).get(diff, {}).get('total', 0) > 0
               for name in method_names):
            valid_difficulties.append(diff)

    if not valid_difficulties:
        valid_difficulties = difficulties

    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(len(valid_difficulties))
    width = 0.25
    colors = ['#3498db', '#2ecc71', '#9b59b6']

    for i, (name, color) in enumerate(zip(method_names, colors)):
        vals = [data[name][difficulties.index(d)] for d in valid_difficulties]
        bars = ax.bar(x + i * width, vals, width, label=name, color=color, edgecolor='black')

    ax.set_xlabel('Problem Difficulty', fontsize=12)
    ax.set_ylabel('Success Rate (%)', fontsize=12)
    ax.set_title('Success Rate by Problem Difficulty', fontsize=14, fontweight='bold')
    ax.set_xticks(x + width)
    ax.set_xticklabels([d.capitalize() for d in valid_difficulties])
    ax.legend()
    ax.set_ylim(0, 100)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'difficulty_breakdown.png'), dpi=150, bbox_inches='tight')
    plt.close()

def plot_refinement_analysis(results, output_dir):
    """Plot analysis of refinement iterations in SpecBridge Dynamic."""
    dynamic_results = results['specbridge_dynamic']

    # Count problems by refinement iterations
    iterations = [r.get('refinement_iterations', 0) for r in dynamic_results]
    success_by_iter = {}
    total_by_iter = {}

    for r in dynamic_results:
        it = r.get('refinement_iterations', 0)
        if it not in success_by_iter:
            success_by_iter[it] = 0
            total_by_iter[it] = 0
        total_by_iter[it] += 1
        if r['success']:
            success_by_iter[it] += 1

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Plot 1: Distribution of refinement iterations
    ax1 = axes[0]
    unique_iters = sorted(set(iterations))
    counts = [iterations.count(i) for i in unique_iters]
    ax1.bar(unique_iters, counts, color='#9b59b6', edgecolor='black')
    ax1.set_xlabel('Number of Refinement Iterations', fontsize=11)
    ax1.set_ylabel('Number of Problems', fontsize=11)
    ax1.set_title('Distribution of Refinement Iterations', fontsize=12, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)

    # Plot 2: Success rate by refinement iterations
    ax2 = axes[1]
    iter_labels = [str(i) for i in unique_iters]
    success_rates = [success_by_iter.get(i, 0) / total_by_iter.get(i, 1) * 100 for i in unique_iters]

    bars = ax2.bar(iter_labels, success_rates, color='#2ecc71', edgecolor='black')
    ax2.set_xlabel('Number of Refinement Iterations', fontsize=11)
    ax2.set_ylabel('Success Rate (%)', fontsize=11)
    ax2.set_title('Success Rate by Refinement Iterations', fontsize=12, fontweight='bold')
    ax2.set_ylim(0, 100)
    ax2.grid(axis='y', alpha=0.3)

    # Add count labels
    for bar, count in zip(bars, [total_by_iter.get(i, 0) for i in unique_iters]):
        ax2.annotate(f'n={count}',
                    xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'refinement_analysis.png'), dpi=150, bbox_inches='tight')
    plt.close()

def plot_time_comparison(metrics, output_dir):
    """Plot average execution time comparison."""
    methods = ['baseline', 'specbridge_static', 'specbridge_dynamic']
    method_names = ['Baseline\n(Direct LLM)', 'SpecBridge\nStatic', 'SpecBridge\nDynamic']
    avg_times = [metrics[m]['avg_time'] for m in methods]

    fig, ax = plt.subplots(figsize=(8, 6))

    colors = ['#3498db', '#2ecc71', '#9b59b6']
    bars = ax.bar(method_names, avg_times, color=colors, edgecolor='black', linewidth=1.5)

    # Add value labels
    for bar, t in zip(bars, avg_times):
        height = bar.get_height()
        ax.annotate(f'{t:.2f}s',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=11, fontweight='bold')

    ax.set_ylabel('Average Time (seconds)', fontsize=12)
    ax.set_title('Average Execution Time per Problem', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'time_comparison.png'), dpi=150, bbox_inches='tight')
    plt.close()

def plot_disagreement_distribution(results, output_dir):
    """Plot disagreement score distribution for ambiguity detection."""
    if 'ambiguity' not in results:
        return

    ambiguity_data = results['ambiguity']
    scores = [a['disagreement_score'] for a in ambiguity_data]

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.hist(scores, bins=10, range=(0, 1), color='#e74c3c', alpha=0.7, edgecolor='black')
    ax.axvline(0.5, color='black', linestyle='--', linewidth=2, label='Ambiguity Threshold (0.5)')
    ax.set_xlabel('Disagreement Score', fontsize=11)
    ax.set_ylabel('Number of Problems', fontsize=11)
    ax.set_title('Specification Disagreement Score Distribution', fontsize=13, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)

    # Add annotation
    num_ambiguous = sum(1 for a in ambiguity_data if a['detected_ambiguous'])
    ax.annotate(f'Detected Ambiguous: {num_ambiguous}/{len(ambiguity_data)}',
                xy=(0.95, 0.95), xycoords='axes fraction',
                ha='right', va='top', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'disagreement_distribution.png'), dpi=150, bbox_inches='tight')
    plt.close()

def plot_learning_curves(results, output_dir):
    """Plot cumulative success rate over problems (learning curve style)."""
    methods = ['baseline', 'specbridge_static', 'specbridge_dynamic']
    method_names = ['Baseline', 'SpecBridge Static', 'SpecBridge Dynamic']
    colors = ['#3498db', '#2ecc71', '#9b59b6']

    fig, ax = plt.subplots(figsize=(10, 6))

    for method, name, color in zip(methods, method_names, colors):
        successes = [r['success'] for r in results[method]]
        cumulative_success = np.cumsum(successes) / (np.arange(len(successes)) + 1) * 100
        ax.plot(range(1, len(cumulative_success) + 1), cumulative_success,
                label=name, color=color, linewidth=2, marker='o', markersize=4)

    ax.set_xlabel('Number of Problems', fontsize=12)
    ax.set_ylabel('Cumulative Success Rate (%)', fontsize=12)
    ax.set_title('Cumulative Success Rate Over Problems', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)
    ax.set_ylim(0, 100)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'learning_curves.png'), dpi=150, bbox_inches='tight')
    plt.close()

def generate_all_plots(results_file, output_dir):
    """Generate all visualization plots."""
    os.makedirs(output_dir, exist_ok=True)

    data = load_results(results_file)
    results = data['results']
    metrics = data['metrics']

    print("Generating success rate comparison...")
    plot_success_rate_comparison(metrics, output_dir)

    print("Generating pass rate distribution...")
    plot_pass_rate_distribution(results, output_dir)

    print("Generating difficulty breakdown...")
    plot_difficulty_breakdown(metrics, output_dir)

    print("Generating refinement analysis...")
    plot_refinement_analysis(results, output_dir)

    print("Generating time comparison...")
    plot_time_comparison(metrics, output_dir)

    print("Generating disagreement distribution...")
    plot_disagreement_distribution(results, output_dir)

    print("Generating learning curves...")
    plot_learning_curves(results, output_dir)

    print(f"\nAll plots saved to {output_dir}")

if __name__ == "__main__":
    import sys
    results_dir = sys.argv[1] if len(sys.argv) > 1 else "outputs"
    results_file = os.path.join(results_dir, 'experiment_results.json')
    generate_all_plots(results_file, results_dir)
