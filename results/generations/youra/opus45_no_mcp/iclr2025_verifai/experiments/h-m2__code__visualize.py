"""H-M2: Visualization - 3 required figures."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os


def generate_all_figures(results: dict, figures_dir: str) -> None:
    """Generate 3 figures: gate comparison, category pie, per-benchmark bars."""
    os.makedirs(figures_dir, exist_ok=True)

    metrics = results.get("metrics", {})
    category_dist = results.get("category_distribution", {})
    per_benchmark = results.get("per_benchmark", {})

    # Figure 1: Gate Metrics Bar Chart (REQUIRED)
    fig1, ax1 = plt.subplots(figsize=(8, 6))
    rate = metrics.get("behavioral_rate", 0)
    threshold = 0.40
    colors = ['green' if rate > threshold else 'red', 'gray']
    ax1.bar(['Behavioral Rate', 'Threshold'], [rate, threshold], color=colors)
    ax1.set_ylabel('Rate')
    ax1.set_title('H-M2: Behavioral Rate vs 40% Threshold')
    ax1.set_ylim(0, 1)
    for i, v in enumerate([rate, threshold]):
        ax1.text(i, v + 0.02, f'{v:.1%}', ha='center', fontweight='bold')
    ax1.axhline(y=threshold, color='orange', linestyle='--', label='Gate Threshold')
    ax1.legend()
    fig1.savefig(os.path.join(figures_dir, 'gate_metrics.png'), dpi=150, bbox_inches='tight')
    plt.close(fig1)

    # Figure 2: Failure Category Pie Chart
    fig2, ax2 = plt.subplots(figsize=(8, 6))
    labels = []
    sizes = []
    for cat, count in category_dist.items():
        if count > 0:
            labels.append(f"{cat} ({count})")
            sizes.append(count)
    if sizes:
        ax2.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax2.set_title('H-M2: Failure Category Distribution')
    else:
        ax2.text(0.5, 0.5, 'No failures to categorize', ha='center', va='center')
        ax2.set_title('H-M2: Failure Category Distribution')
    fig2.savefig(os.path.join(figures_dir, 'category_breakdown.png'), dpi=150, bbox_inches='tight')
    plt.close(fig2)

    # Figure 3: Per-Benchmark Bar Chart
    fig3, ax3 = plt.subplots(figsize=(8, 6))
    benchmarks = ['HumanEval+', 'MBPP+']
    he_rate = per_benchmark.get("humaneval_plus", {}).get("behavioral_rate", 0)
    mbpp_rate = per_benchmark.get("mbpp_plus", {}).get("behavioral_rate", 0)
    rates = [he_rate, mbpp_rate]
    bars = ax3.bar(benchmarks, rates, color=['steelblue', 'coral'])
    ax3.set_ylabel('Behavioral Rate')
    ax3.set_title('H-M2: Per-Benchmark Behavioral Rates')
    ax3.set_ylim(0, 1)
    ax3.axhline(y=0.40, color='orange', linestyle='--', label='Gate Threshold (40%)')
    for bar, v in zip(bars, rates):
        ax3.text(bar.get_x() + bar.get_width()/2, v + 0.02, f'{v:.1%}', ha='center')
    ax3.legend()
    fig3.savefig(os.path.join(figures_dir, 'per_benchmark.png'), dpi=150, bbox_inches='tight')
    plt.close(fig3)

    print(f"Saved 3 figures to {figures_dir}")
