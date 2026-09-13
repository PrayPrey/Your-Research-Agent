import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

def plot_gate_metrics(metrics: dict, save_path: str) -> None:
    """Plot target vs actual for gate metrics."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Time comparison
    time_target_min = metrics['time_target'] / 60
    time_actual_min = metrics['time_actual'] / 60

    axes[0].bar(['Target', 'Actual'],
                [time_target_min, time_actual_min],
                color=['green', 'blue' if metrics['time_pass'] else 'red'])
    axes[0].set_ylabel('Time (minutes)')
    axes[0].set_title('Computational Time')
    axes[0].axhline(y=time_target_min, color='red', linestyle='--', label='Threshold', alpha=0.5)
    axes[0].legend()

    # Latency comparison
    axes[1].bar(['Target', 'Actual'],
                [metrics['latency_target'], metrics['latency_actual']],
                color=['green', 'blue' if metrics['latency_pass'] else 'red'])
    axes[1].set_ylabel('Latency (ms)')
    axes[1].set_title('AST Parse Latency')
    axes[1].axhline(y=metrics['latency_target'], color='red', linestyle='--', label='Threshold', alpha=0.5)
    axes[1].legend()

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved gate metrics figure to {save_path}")

def plot_ast_latency_dist(latencies: list[float], save_path: str) -> None:
    """Plot AST latency distribution histogram."""
    plt.figure(figsize=(10, 6))
    plt.hist(latencies, bins=30, edgecolor='black', alpha=0.7)
    plt.xlabel('Latency (ms)')
    plt.ylabel('Count')
    plt.title('AST Parse Latency Distribution')
    plt.axvline(x=50, color='red', linestyle='--', label='Target (50ms)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved latency distribution to {save_path}")
