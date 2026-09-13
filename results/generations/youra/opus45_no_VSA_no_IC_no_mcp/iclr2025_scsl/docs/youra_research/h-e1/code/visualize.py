import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os


def plot_ratio_over_epochs(epoch_ratios: list, save_path: str) -> None:
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    epochs = [e for e, _ in epoch_ratios]
    ratios = [r for _, r in epoch_ratios]

    plt.figure(figsize=(10, 6))
    plt.plot(epochs, ratios, 'b-o', linewidth=2, markersize=4)
    plt.axhline(y=1.0, color='r', linestyle='--', label='Dominance threshold (ratio=1.0)')
    plt.axvline(x=10, color='g', linestyle='--', alpha=0.7, label='Gate threshold (epoch 10)')

    plt.xlabel('Epoch', fontsize=12)
    plt.ylabel('Spurious/Core Attribution Ratio', fontsize=12)
    plt.title('Spurious vs Core Feature Attribution Over Training', fontsize=14)
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved ratio plot to {save_path}")


def plot_gate_comparison(gate_result: dict, save_path: str) -> None:
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 5))

    metrics = ['Dominance Epoch', 'Attribution Ratio']
    targets = [10, 1.0]
    actuals = [
        gate_result.get('dominance_epoch', 50) or 50,
        gate_result.get('ratio_at_dominance', 0) or 0
    ]

    x = range(len(metrics))
    width = 0.35

    bars1 = ax.bar([i - width/2 for i in x], targets, width, label='Target', color='lightblue', edgecolor='navy')
    bars2 = ax.bar([i + width/2 for i in x], actuals, width, label='Actual', color='lightgreen' if gate_result['pass'] else 'salmon', edgecolor='darkgreen' if gate_result['pass'] else 'darkred')

    ax.set_xlabel('Metric', fontsize=12)
    ax.set_ylabel('Value', fontsize=12)
    ax.set_title(f"Gate Check: {'PASS' if gate_result['pass'] else 'FAIL'}", fontsize=14, fontweight='bold', color='green' if gate_result['pass'] else 'red')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.legend()

    for bar in bars1 + bars2:
        height = bar.get_height()
        ax.annotate(f'{height:.2f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved gate comparison to {save_path}")
