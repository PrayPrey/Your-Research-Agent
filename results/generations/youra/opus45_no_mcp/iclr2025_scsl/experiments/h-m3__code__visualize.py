"""H-M3 Visualization: 6 required figures for detection validation"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


def plot_gate_metrics(gate_result: dict, save_path: str) -> None:
    """Bar chart comparing target vs actual metrics."""
    fig, ax = plt.subplots(figsize=(10, 6))
    metrics = ['detection_rate', 'snr']
    targets = [gate_result['detection_rate']['target'], gate_result['snr']['target']]
    actuals = [gate_result['detection_rate']['value'], gate_result['snr']['value']]
    x = np.arange(len(metrics))
    width = 0.35
    ax.bar(x - width/2, targets, width, label='Target', color='#2196F3', alpha=0.8)
    ax.bar(x + width/2, actuals, width, label='Actual', color='#4CAF50' if gate_result['passed'] else '#F44336', alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.set_ylabel('Value')
    ax.set_title(f"Gate Metrics - {'PASS' if gate_result['passed'] else 'FAIL'}")
    ax.legend()
    ax.axhline(y=0.8, color='gray', linestyle='--', alpha=0.5)
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)


def plot_wga_with_derivatives(wga: np.ndarray, smoothed: np.ndarray, d2: np.ndarray,
                               peak_epoch: int, save_path: str) -> None:
    """3-panel plot: raw WGA, smoothed, d²WGA/dt² with peak marked."""
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    epochs = np.arange(len(wga))
    axes[0].plot(epochs, wga, 'b-', linewidth=1.5, label='Raw WGA')
    axes[0].set_ylabel('WGA')
    axes[0].set_title('Worst-Group Accuracy')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    axes[1].plot(epochs, smoothed, 'g-', linewidth=1.5, label='Smoothed WGA')
    axes[1].set_ylabel('Smoothed WGA')
    axes[1].set_title('Smoothed WGA (5-epoch window)')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    axes[2].plot(epochs, d2, 'r-', linewidth=1.5, label='d²WGA/dt²')
    if peak_epoch is not None and 0 <= peak_epoch < len(d2):
        axes[2].axvline(x=peak_epoch, color='orange', linestyle='--', linewidth=2, label=f'Peak @ epoch {peak_epoch}')
        axes[2].scatter([peak_epoch], [d2[peak_epoch]], color='orange', s=100, zorder=5)
    axes[2].set_xlabel('Epoch')
    axes[2].set_ylabel('d²WGA/dt²')
    axes[2].set_title('Second Derivative with Crystallization Peak')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)
    fig.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)


def plot_window_comparison(wga: np.ndarray, windows: list, save_path: str) -> None:
    """Overlay d²WGA/dt² for different smoothing windows."""
    from detector import smooth_curve, second_derivative
    fig, ax = plt.subplots(figsize=(12, 6))
    epochs = np.arange(len(wga))
    colors = ['#2196F3', '#4CAF50', '#FF9800']
    for i, w in enumerate(windows):
        smoothed = smooth_curve(wga, w)
        d2 = second_derivative(smoothed)
        ax.plot(epochs, d2, linewidth=1.5, color=colors[i % len(colors)],
                label=f'Window={w}', alpha=0.8)
    ax.set_xlabel('Epoch')
    ax.set_ylabel('d²WGA/dt²')
    ax.set_title('Second Derivative: Window Size Comparison')
    ax.legend()
    ax.grid(True, alpha=0.3)
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)


def plot_detection_heatmap(all_results: dict, save_path: str) -> None:
    """Seeds x Benchmarks heatmap showing detected peak epochs."""
    benchmarks = sorted(set(r['benchmark'] for r in all_results))
    n_seeds = max(r['seed'] for r in all_results) + 1
    data = np.full((n_seeds, len(benchmarks)), np.nan)
    for r in all_results:
        seed = r['seed']
        bm_idx = benchmarks.index(r['benchmark'])
        if r['detected'] and r['epoch'] is not None:
            data[seed, bm_idx] = r['epoch']
    fig, ax = plt.subplots(figsize=(10, 6))
    cmap = plt.cm.viridis.copy()
    cmap.set_bad(color='lightgray')
    im = ax.imshow(data, cmap=cmap, aspect='auto')
    ax.set_xticks(range(len(benchmarks)))
    ax.set_xticklabels(benchmarks)
    ax.set_yticks(range(n_seeds))
    ax.set_yticklabels([f'Seed {i}' for i in range(n_seeds)])
    ax.set_xlabel('Benchmark')
    ax.set_ylabel('Seed')
    ax.set_title('Detected Crystallization Epoch (gray = not detected)')
    cbar = fig.colorbar(im, ax=ax, label='Epoch')
    for i in range(n_seeds):
        for j in range(len(benchmarks)):
            if not np.isnan(data[i, j]):
                ax.text(j, i, f'{int(data[i, j])}', ha='center', va='center', color='white', fontsize=9)
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)


def plot_snr_distribution(all_results: dict, save_path: str) -> None:
    """Box plot of SNR values across conditions."""
    benchmarks = sorted(set(r['benchmark'] for r in all_results))
    snr_data = {bm: [] for bm in benchmarks}
    for r in all_results:
        if r['detected'] and r['snr'] is not None:
            snr_data[r['benchmark']].append(r['snr'])
    fig, ax = plt.subplots(figsize=(10, 6))
    data_to_plot = [snr_data[bm] if snr_data[bm] else [0] for bm in benchmarks]
    bp = ax.boxplot(data_to_plot, patch_artist=True)
    ax.set_xticks(range(1, len(benchmarks) + 1))
    ax.set_xticklabels(benchmarks)
    colors = ['#2196F3', '#4CAF50', '#FF9800']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
    ax.axhline(y=2.0, color='red', linestyle='--', linewidth=2, label='Target SNR (2.0)')
    ax.set_xlabel('Benchmark')
    ax.set_ylabel('Signal-to-Noise Ratio')
    ax.set_title('SNR Distribution Across Benchmarks')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)


def plot_timing_variance(aggregated: dict, save_path: str) -> None:
    """Bar chart showing peak timing variance per benchmark."""
    benchmarks = list(aggregated.keys())
    variances = [aggregated[bm]['timing_variance_epochs'] for bm in benchmarks]
    variances = [v if v != float('inf') else 0 for v in variances]
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ['#2196F3', '#4CAF50', '#FF9800']
    bars = ax.bar(benchmarks, variances, color=colors[:len(benchmarks)], alpha=0.8)
    ax.axhline(y=5.0, color='red', linestyle='--', linewidth=2, label='Target (<5 epochs)')
    ax.set_xlabel('Benchmark')
    ax.set_ylabel('Timing Variance (epochs)')
    ax.set_title('Peak Timing Variance Across Seeds')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    for bar, v in zip(bars, variances):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f'{v:.2f}', ha='center', va='bottom', fontsize=10)
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
