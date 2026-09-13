"""
Visualization script for experiment results
"""
import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from evaluation import Evaluator
import config

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 11

def load_results():
    """Load experiment results"""
    evaluator = Evaluator()
    evaluator.load_results("all_results.json")
    return evaluator

def plot_model_comparison(evaluator: Evaluator):
    """Plot comparison of different methods"""
    all_metrics = evaluator.compute_all_metrics()

    methods = list(all_metrics.keys())
    repair_success = [all_metrics[m]['repair_success_rate'] for m in methods]
    avg_iterations = [all_metrics[m]['average_repair_iterations'] for m in methods]
    test_pass_rate = [all_metrics[m]['avg_test_pass_rate'] for m in methods]

    # Create figure with subplots
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Plot 1: Repair Success Rate
    axes[0].bar(methods, repair_success, color=['#ff6b6b', '#feca57', '#48dbfb', '#1dd1a1'])
    axes[0].set_ylabel('Repair Success Rate')
    axes[0].set_title('Repair Success Rate by Method')
    axes[0].set_ylim(0, 1.0)
    axes[0].tick_params(axis='x', rotation=45)
    for i, v in enumerate(repair_success):
        axes[0].text(i, v + 0.02, f'{v:.3f}', ha='center', va='bottom')

    # Plot 2: Average Repair Iterations
    axes[1].bar(methods, avg_iterations, color=['#ff6b6b', '#feca57', '#48dbfb', '#1dd1a1'])
    axes[1].set_ylabel('Average Iterations')
    axes[1].set_title('Average Repair Iterations by Method')
    axes[1].tick_params(axis='x', rotation=45)
    for i, v in enumerate(avg_iterations):
        if v > 0:
            axes[1].text(i, v + 0.1, f'{v:.2f}', ha='center', va='bottom')

    # Plot 3: Test Pass Rate
    axes[2].bar(methods, test_pass_rate, color=['#ff6b6b', '#feca57', '#48dbfb', '#1dd1a1'])
    axes[2].set_ylabel('Test Pass Rate')
    axes[2].set_title('Average Test Pass Rate by Method')
    axes[2].set_ylim(0, 1.0)
    axes[2].tick_params(axis='x', rotation=45)
    for i, v in enumerate(test_pass_rate):
        axes[2].text(i, v + 0.02, f'{v:.3f}', ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig('model_comparison.png', dpi=300, bbox_inches='tight')
    print("Saved: model_comparison.png")
    plt.close()

def plot_learning_curves(evaluator: Evaluator):
    """Plot learning curves for each method"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    methods = config.BASELINES
    colors = ['#ff6b6b', '#feca57', '#48dbfb', '#1dd1a1']

    for idx, method in enumerate(methods):
        iterations, success_rates = evaluator.get_learning_curve_data(method)

        if iterations and success_rates:
            axes[idx].plot(iterations, success_rates, marker='o', linewidth=2,
                          markersize=6, color=colors[idx])
            axes[idx].set_xlabel('Iteration')
            axes[idx].set_ylabel('Cumulative Success Rate')
            axes[idx].set_title(f'Learning Curve: {method}')
            axes[idx].grid(True, alpha=0.3)
            axes[idx].set_ylim(0, 1.0)

            # Add value labels at key points
            for i, (x, y) in enumerate(zip(iterations, success_rates)):
                if i % 2 == 0 or i == len(iterations) - 1:
                    axes[idx].text(x, y + 0.02, f'{y:.2f}', ha='center', fontsize=9)

    plt.tight_layout()
    plt.savefig('learning_curve_comparison.png', dpi=300, bbox_inches='tight')
    print("Saved: learning_curve_comparison.png")
    plt.close()

def plot_error_types(evaluator: Evaluator):
    """Plot distribution of error types"""
    # For each method, count successful vs failed problems
    methods = config.BASELINES
    success_counts = []
    failure_counts = []

    for method in methods:
        results = [r for r in evaluator.results if r.method == method]
        success_counts.append(sum(1 for r in results if r.success))
        failure_counts.append(sum(1 for r in results if not r.success))

    x = np.arange(len(methods))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    bars1 = ax.bar(x - width/2, success_counts, width, label='Success',
                   color='#1dd1a1', alpha=0.8)
    bars2 = ax.bar(x + width/2, failure_counts, width, label='Failure',
                   color='#ff6b6b', alpha=0.8)

    ax.set_xlabel('Method')
    ax.set_ylabel('Number of Problems')
    ax.set_title('Success vs Failure by Method')
    ax.set_xticks(x)
    ax.set_xticklabels(methods, rotation=45, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}', ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig('success_failure_comparison.png', dpi=300, bbox_inches='tight')
    print("Saved: success_failure_comparison.png")
    plt.close()

def plot_iteration_distribution(evaluator: Evaluator):
    """Plot distribution of iterations needed for successful repairs"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    methods = config.BASELINES
    colors = ['#ff6b6b', '#feca57', '#48dbfb', '#1dd1a1']

    for idx, method in enumerate(methods):
        results = [r for r in evaluator.results if r.method == method and r.success]

        if results:
            iterations = [r.num_iterations for r in results]
            unique_iters = sorted(set(iterations))
            counts = [iterations.count(i) for i in unique_iters]

            axes[idx].bar(unique_iters, counts, color=colors[idx], alpha=0.7)
            axes[idx].set_xlabel('Number of Iterations')
            axes[idx].set_ylabel('Frequency')
            axes[idx].set_title(f'Iteration Distribution: {method}')
            axes[idx].grid(True, alpha=0.3, axis='y')

            # Add value labels
            for x, y in zip(unique_iters, counts):
                axes[idx].text(x, y + 0.1, str(y), ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig('iteration_distribution.png', dpi=300, bbox_inches='tight')
    print("Saved: iteration_distribution.png")
    plt.close()

def plot_test_pass_progression(evaluator: Evaluator):
    """Plot how test pass rates improve with iterations"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    methods = config.BASELINES
    colors = ['#ff6b6b', '#feca57', '#48dbfb', '#1dd1a1']

    for idx, method in enumerate(methods):
        results = [r for r in evaluator.results if r.method == method]

        # Average test pass rate at each iteration
        max_iter = max((r.num_iterations for r in results), default=0)
        if max_iter == 0:
            continue

        iter_test_rates = {i: [] for i in range(1, max_iter + 1)}

        for result in results:
            for hist in result.iteration_history:
                iter_num = hist['iteration']
                if iter_num <= max_iter:
                    iter_test_rates[iter_num].append(hist['test_pass_rate'])

        iterations = sorted(iter_test_rates.keys())
        avg_rates = [np.mean(iter_test_rates[i]) if iter_test_rates[i] else 0
                    for i in iterations]

        if iterations:
            axes[idx].plot(iterations, avg_rates, marker='o', linewidth=2,
                          markersize=6, color=colors[idx])
            axes[idx].set_xlabel('Iteration')
            axes[idx].set_ylabel('Average Test Pass Rate')
            axes[idx].set_title(f'Test Pass Rate Progression: {method}')
            axes[idx].grid(True, alpha=0.3)
            axes[idx].set_ylim(0, 1.0)

    plt.tight_layout()
    plt.savefig('test_pass_progression.png', dpi=300, bbox_inches='tight')
    print("Saved: test_pass_progression.png")
    plt.close()

def main():
    """Generate all visualizations"""
    print("Loading results...")
    evaluator = load_results()

    print("\nGenerating visualizations...")
    plot_model_comparison(evaluator)
    plot_learning_curves(evaluator)
    plot_error_types(evaluator)
    plot_iteration_distribution(evaluator)
    plot_test_pass_progression(evaluator)

    print("\nAll visualizations generated successfully!")

if __name__ == "__main__":
    main()
