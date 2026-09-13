import matplotlib.pyplot as plt
import numpy as np
import os


def plot_ccr_by_strategy(ccr_results: dict, out_dir: str) -> str:
    """Bar chart: CCR by filtering strategy."""
    strategies = list(ccr_results.keys())
    means = [np.mean(list(ccr_results[s].values())) for s in strategies]
    stds = [np.std(list(ccr_results[s].values())) for s in strategies]

    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(strategies))
    bars = ax.bar(x, means, yerr=stds, capsize=5, color=['#2ecc71', '#3498db', '#e74c3c'])
    ax.set_xticks(x)
    ax.set_xticklabels(strategies)
    ax.set_ylabel('CCR (Contamination Coverage Ratio)')
    ax.set_title('CCR by Filtering Strategy')
    ax.set_ylim(0, max(means) * 1.3 if means else 1)

    for bar, mean in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{mean:.3f}', ha='center', va='bottom', fontsize=10)

    path = os.path.join(out_dir, 'ccr_by_strategy.png')
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def plot_ccr_boxplot(ccr_results: dict, out_dir: str) -> str:
    """Box plot: CCR distribution across seeds."""
    strategies = list(ccr_results.keys())
    data = [list(ccr_results[s].values()) for s in strategies]

    fig, ax = plt.subplots(figsize=(8, 5))
    bp = ax.boxplot(data, labels=strategies, patch_artist=True)
    colors = ['#2ecc71', '#3498db', '#e74c3c']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax.set_ylabel('CCR')
    ax.set_title('CCR Distribution by Strategy')

    path = os.path.join(out_dir, 'ccr_boxplot.png')
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def plot_bootstrap_histogram(diffs: np.ndarray, mean_diff: float,
                              p_value: float, out_dir: str) -> str:
    """Histogram of bootstrap CCR differences."""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(diffs, bins=50, color='#3498db', alpha=0.7, edgecolor='black')
    ax.axvline(0, color='red', linestyle='--', linewidth=2, label='No difference')
    ax.axvline(mean_diff, color='green', linestyle='-', linewidth=2,
               label=f'Observed diff: {mean_diff:.3f}')

    ax.set_xlabel('CCR(perplexity) - CCR(random)')
    ax.set_ylabel('Frequency')
    ax.set_title(f'Bootstrap Distribution (p={p_value:.4f})')
    ax.legend()

    path = os.path.join(out_dir, 'bootstrap_histogram.png')
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def plot_gate_metrics(target: dict, actual: dict, out_dir: str) -> str:
    """Bar chart comparing target vs actual gate metrics."""
    metrics = list(target.keys())
    target_vals = [target[m] for m in metrics]
    actual_vals = [actual[m] for m in metrics]

    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(metrics))
    width = 0.35

    bars1 = ax.bar(x - width/2, target_vals, width, label='Target', color='#95a5a6')
    bars2 = ax.bar(x + width/2, actual_vals, width, label='Actual', color='#2ecc71')

    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.set_ylabel('Value')
    ax.set_title('Gate Metrics: Target vs Actual')
    ax.legend()

    # Add pass/fail indicators
    for i, (t, a) in enumerate(zip(target_vals, actual_vals)):
        status = '✓' if a >= t else '✗'
        ax.text(x[i] + width/2, a + 0.02, status, ha='center', va='bottom',
                fontsize=14, color='green' if a >= t else 'red')

    path = os.path.join(out_dir, 'gate_metrics.png')
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return path
