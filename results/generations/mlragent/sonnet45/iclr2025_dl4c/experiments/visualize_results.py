"""
Visualization script for experiment results.
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List
import os


def load_results(filename: str = "experiment_results.json") -> Dict:
    """Load experiment results from JSON file."""
    with open(filename, "r") as f:
        return json.load(f)


def create_visualizations(results: Dict, output_dir: str = "figures"):
    """Create all visualizations."""
    os.makedirs(output_dir, exist_ok=True)

    # 1. Success Rate Comparison
    plot_success_rates(results, output_dir)

    # 2. Average Attempts Comparison
    plot_average_attempts(results, output_dir)

    # 3. Success by Attempt Number
    plot_success_by_attempt(results, output_dir)

    # 4. Time Efficiency
    plot_time_efficiency(results, output_dir)

    # 5. Counterfactual Statistics (for SECACE)
    plot_counterfactual_stats(results, output_dir)

    # 6. Task-wise Performance
    plot_taskwise_performance(results, output_dir)

    print(f"All visualizations saved to {output_dir}/")


def plot_success_rates(results: Dict, output_dir: str):
    """Plot success rates for each method."""
    methods = []
    success_rates = []

    for method, method_results in results.items():
        total = len(method_results)
        successful = sum(1 for r in method_results if r.get("success", False))
        success_rate = (successful / total * 100) if total > 0 else 0

        methods.append(method.replace("_", " ").title())
        success_rates.append(success_rate)

    plt.figure(figsize=(10, 6))
    bars = plt.bar(methods, success_rates, color=['#3498db', '#e74c3c', '#2ecc71'])

    plt.ylabel('Success Rate (%)', fontsize=12)
    plt.title('Success Rate Comparison Across Methods', fontsize=14, fontweight='bold')
    plt.ylim(0, 100)

    # Add value labels on bars
    for i, (bar, rate) in enumerate(zip(bars, success_rates)):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                f'{rate:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')

    plt.grid(axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    plt.savefig(f"{output_dir}/success_rate_comparison.png", dpi=300, bbox_inches='tight')
    plt.close()


def plot_average_attempts(results: Dict, output_dir: str):
    """Plot average number of attempts for each method."""
    methods = []
    avg_attempts = []
    std_attempts = []

    for method, method_results in results.items():
        attempts_list = [r.get("attempts", 0) for r in method_results]
        avg = np.mean(attempts_list) if attempts_list else 0
        std = np.std(attempts_list) if attempts_list else 0

        methods.append(method.replace("_", " ").title())
        avg_attempts.append(avg)
        std_attempts.append(std)

    plt.figure(figsize=(10, 6))
    bars = plt.bar(methods, avg_attempts, yerr=std_attempts, capsize=5,
                   color=['#3498db', '#e74c3c', '#2ecc71'], alpha=0.8)

    plt.ylabel('Average Number of Attempts', fontsize=12)
    plt.title('Average Attempts to Solution', fontsize=14, fontweight='bold')

    # Add value labels on bars
    for bar, avg in zip(bars, avg_attempts):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f'{avg:.2f}', ha='center', va='bottom', fontsize=11)

    plt.grid(axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    plt.savefig(f"{output_dir}/average_attempts.png", dpi=300, bbox_inches='tight')
    plt.close()


def plot_success_by_attempt(results: Dict, output_dir: str):
    """Plot cumulative success rate by attempt number."""
    plt.figure(figsize=(12, 6))

    for method, method_results in results.items():
        max_attempts = 5
        cumulative_success = []

        for attempt_num in range(1, max_attempts + 1):
            # Count tasks solved within this many attempts
            solved = sum(1 for r in method_results
                        if r.get("success", False) and r.get("attempts", 0) <= attempt_num)
            cumulative_success.append(solved / len(method_results) * 100 if method_results else 0)

        plt.plot(range(1, max_attempts + 1), cumulative_success,
                marker='o', linewidth=2, markersize=8,
                label=method.replace("_", " ").title())

    plt.xlabel('Number of Attempts', fontsize=12)
    plt.ylabel('Cumulative Success Rate (%)', fontsize=12)
    plt.title('Success Rate vs. Number of Attempts', fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.xticks(range(1, 6))
    plt.ylim(0, 100)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/success_by_attempt.png", dpi=300, bbox_inches='tight')
    plt.close()


def plot_time_efficiency(results: Dict, output_dir: str):
    """Plot time efficiency for each method."""
    methods = []
    avg_times = []
    std_times = []

    for method, method_results in results.items():
        successful_results = [r for r in method_results if r.get("success", False)]
        times = [r.get("elapsed_time", 0) for r in successful_results]

        avg = np.mean(times) if times else 0
        std = np.std(times) if times else 0

        methods.append(method.replace("_", " ").title())
        avg_times.append(avg)
        std_times.append(std)

    plt.figure(figsize=(10, 6))
    bars = plt.bar(methods, avg_times, yerr=std_times, capsize=5,
                   color=['#3498db', '#e74c3c', '#2ecc71'], alpha=0.8)

    plt.ylabel('Average Time (seconds)', fontsize=12)
    plt.title('Average Time to Solution (Successful Tasks)', fontsize=14, fontweight='bold')

    # Add value labels on bars
    for bar, avg in zip(bars, avg_times):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(std_times)/10,
                f'{avg:.1f}s', ha='center', va='bottom', fontsize=11)

    plt.grid(axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    plt.savefig(f"{output_dir}/time_efficiency.png", dpi=300, bbox_inches='tight')
    plt.close()


def plot_counterfactual_stats(results: Dict, output_dir: str):
    """Plot counterfactual generation statistics for SECACE."""
    if "secace" not in results:
        return

    secace_results = results["secace"]

    # Counterfactuals generated per task
    cf_counts = [r.get("counterfactuals_generated", 0) for r in secace_results]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Histogram of counterfactuals generated
    ax1.hist(cf_counts, bins=range(0, max(cf_counts) + 2), color='#2ecc71', alpha=0.7, edgecolor='black')
    ax1.set_xlabel('Number of Counterfactuals Generated', fontsize=11)
    ax1.set_ylabel('Number of Tasks', fontsize=11)
    ax1.set_title('Distribution of Counterfactuals per Task', fontsize=12, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3, linestyle='--')

    # Success vs. counterfactuals generated
    successful_tasks = [r for r in secace_results if r.get("success", False)]
    failed_tasks = [r for r in secace_results if not r.get("success", False)]

    avg_cf_success = np.mean([r.get("counterfactuals_generated", 0) for r in successful_tasks]) \
        if successful_tasks else 0
    avg_cf_failed = np.mean([r.get("counterfactuals_generated", 0) for r in failed_tasks]) \
        if failed_tasks else 0

    ax2.bar(['Successful Tasks', 'Failed Tasks'], [avg_cf_success, avg_cf_failed],
            color=['#2ecc71', '#e74c3c'], alpha=0.8)
    ax2.set_ylabel('Avg Counterfactuals Generated', fontsize=11)
    ax2.set_title('Counterfactuals: Success vs. Failure', fontsize=12, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3, linestyle='--')

    # Add value labels
    for i, (val, label) in enumerate(zip([avg_cf_success, avg_cf_failed],
                                         ['Successful Tasks', 'Failed Tasks'])):
        ax2.text(i, val + 0.2, f'{val:.1f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

    plt.tight_layout()
    plt.savefig(f"{output_dir}/counterfactual_statistics.png", dpi=300, bbox_inches='tight')
    plt.close()


def plot_taskwise_performance(results: Dict, output_dir: str):
    """Plot performance comparison for each task."""
    num_tasks = len(results[list(results.keys())[0]])

    task_ids = list(range(1, num_tasks + 1))
    methods = list(results.keys())

    fig, ax = plt.subplots(figsize=(14, 6))

    x = np.arange(len(task_ids))
    width = 0.25

    for i, method in enumerate(methods):
        method_results = results[method]
        success_list = [1 if r.get("success", False) else 0 for r in method_results]

        offset = (i - 1) * width
        ax.bar(x + offset, success_list, width, label=method.replace("_", " ").title(),
               alpha=0.8)

    ax.set_xlabel('Task ID', fontsize=12)
    ax.set_ylabel('Success (1) / Failure (0)', fontsize=12)
    ax.set_title('Task-wise Performance Comparison', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(task_ids)
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_ylim(0, 1.2)

    plt.tight_layout()
    plt.savefig(f"{output_dir}/taskwise_performance.png", dpi=300, bbox_inches='tight')
    plt.close()


def main():
    """Main entry point for visualization."""
    print("Loading experiment results...")
    results = load_results()

    print("Creating visualizations...")
    create_visualizations(results, output_dir="figures")

    print("Visualizations complete!")


if __name__ == "__main__":
    main()
