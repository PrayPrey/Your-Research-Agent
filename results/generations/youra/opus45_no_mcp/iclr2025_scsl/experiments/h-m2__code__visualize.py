import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def plot_probe_accuracy_timeline(spurious_history: list, core_history: list,
                                  epochs: list, crystallization_epoch: int, save_path: str) -> None:
    plt.figure(figsize=(10, 6))
    plt.plot(epochs, spurious_history, 'r-o', label='Spurious Probe Acc', linewidth=2)
    plt.plot(epochs, core_history, 'b-s', label='Core Probe Acc', linewidth=2)
    plt.axvline(x=crystallization_epoch, color='gray', linestyle='--', label='Crystallization')
    plt.xlabel('Epoch')
    plt.ylabel('Probe Accuracy')
    plt.title('Feature Probe Accuracy Timeline')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()

def plot_gate_metrics_comparison(commitment_result: dict, save_path: str) -> None:
    fig, ax = plt.subplots(figsize=(8, 6))
    metrics = ['Spurious Initial', 'Spurious Final', 'Core Final']
    values = [commitment_result['spurious_initial'],
              commitment_result['spurious_final'],
              commitment_result['core_final']]
    colors = ['lightcoral', 'darkred', 'steelblue']
    bars = ax.bar(metrics, values, color=colors)
    ax.axhline(y=0.85, color='gray', linestyle='--', label='Core Threshold (0.85)')
    ax.set_ylabel('Accuracy')
    ax.set_title(f"Gate Result: {'PASS' if commitment_result['gate_pass'] else 'FAIL'}\n"
                 f"Committed: {commitment_result['committed']}, Core Suppressed: {commitment_result['core_suppressed']}")
    ax.set_ylim(0, 1)
    ax.legend()
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, f'{val:.3f}',
                ha='center', va='bottom', fontsize=10)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()

def plot_commitment_summary(spurious_history: list, core_history: list,
                            epochs: list, commitment_result: dict, save_path: str) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    ax1.plot(epochs, spurious_history, 'r-o', label='Spurious', linewidth=2, markersize=8)
    ax1.plot(epochs, core_history, 'b-s', label='Core', linewidth=2, markersize=8)
    ax1.fill_between(epochs, spurious_history, alpha=0.2, color='red')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Probe Accuracy')
    ax1.set_title('Probe Accuracy Over Time')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    labels = ['Committed', 'Core Suppressed', 'Gate Pass']
    vals = [1 if commitment_result['committed'] else 0,
            1 if commitment_result['core_suppressed'] else 0,
            1 if commitment_result['gate_pass'] else 0]
    colors = ['green' if v else 'red' for v in vals]
    ax2.barh(labels, vals, color=colors)
    ax2.set_xlim(0, 1.5)
    ax2.set_title(f"Commitment Analysis\nTrend: {commitment_result['spurious_trend']}")
    for i, v in enumerate(vals):
        ax2.text(v + 0.1, i, 'YES' if v else 'NO', va='center', fontsize=12, fontweight='bold')

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
