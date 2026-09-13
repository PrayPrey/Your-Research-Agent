# visualize.py - h-m3: RCI flip pattern visualizations
import os
import numpy as np
import matplotlib.pyplot as plt
from config import CONFIG


def plot_gate_metrics(rates, save_path=None):
    """Bar chart: hallucination flip rate vs correct flip rate with thresholds."""
    save_path = save_path or os.path.join(CONFIG["figures_dir"], "gate_metrics.png")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 5))

    labels = ["Hallucination", "Correct"]
    values = [rates["hallucination_flip_rate"], rates["correct_flip_rate"]]
    colors = ["red", "green"]

    bars = ax.bar(labels, values, color=colors, alpha=0.7, edgecolor="black")

    # Threshold lines
    ax.axhline(y=CONFIG["halluc_rate_threshold"], color="red", linestyle="--",
               alpha=0.7, label=f"Halluc threshold ({CONFIG['halluc_rate_threshold']:.0%})")
    ax.axhline(y=CONFIG["correct_rate_threshold"], color="green", linestyle="--",
               alpha=0.7, label=f"Correct threshold ({CONFIG['correct_rate_threshold']:.0%})")

    ax.set_ylabel("Flip Rate")
    ax.set_title("RCI Flip Pattern: Gate Metrics")
    ax.set_ylim(0, max(0.5, max(values) * 1.2))
    ax.legend()

    # Add value labels
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f"{val:.1%}", ha="center", va="bottom", fontsize=12)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    return save_path


def plot_flip_position_heatmap(results, save_path=None, max_samples=200):
    """Heatmap: layer index vs sample showing where flips occur."""
    save_path = save_path or os.path.join(CONFIG["figures_dir"], "flip_heatmap.png")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    layer_start, layer_end = CONFIG["layer_range"]
    n_layers = layer_end - layer_start  # transitions = layers - 1

    # Build flip matrix
    samples = results[:max_samples] if len(results) > max_samples else results
    flip_matrix = np.zeros((len(samples), n_layers))

    for i, r in enumerate(samples):
        for pos in r.get("flip_positions", []):
            layer_idx = pos - layer_start
            if 0 <= layer_idx < n_layers:
                flip_matrix[i, layer_idx] = 1

    fig, ax = plt.subplots(figsize=(10, 6))
    im = ax.imshow(flip_matrix.T, aspect="auto", cmap="Reds", vmin=0, vmax=1)
    ax.set_xlabel("Sample")
    ax.set_ylabel("Layer Transition")
    ax.set_yticks(range(n_layers))
    ax.set_yticklabels([f"L{i}→L{i+1}" for i in range(layer_start, layer_end)])
    ax.set_title("RCI Flip Position Heatmap")
    plt.colorbar(im, ax=ax, label="Flip (0/1)")

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    return save_path


def plot_flip_distribution(results, save_path=None):
    """Histogram: number of flips per sample (halluc vs correct)."""
    save_path = save_path or os.path.join(CONFIG["figures_dir"], "flip_distribution.png")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    halluc_flips = [r["num_flips"] for r in results if r["is_hallucination"]]
    correct_flips = [r["num_flips"] for r in results if not r["is_hallucination"]]

    fig, ax = plt.subplots(figsize=(8, 5))
    bins = range(0, max(max(halluc_flips, default=0), max(correct_flips, default=0)) + 2)

    ax.hist(halluc_flips, bins=bins, alpha=0.6, label="Hallucination", color="red", density=True)
    ax.hist(correct_flips, bins=bins, alpha=0.6, label="Correct", color="green", density=True)
    ax.set_xlabel("Number of Flips")
    ax.set_ylabel("Density")
    ax.set_title("RCI Flip Count Distribution")
    ax.legend()

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    return save_path


def plot_layer_flip_rates(results, save_path=None):
    """Bar chart: flip rate per layer transition."""
    save_path = save_path or os.path.join(CONFIG["figures_dir"], "layer_flip_rates.png")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    layer_start, layer_end = CONFIG["layer_range"]
    n_transitions = layer_end - layer_start

    halluc_counts = np.zeros(n_transitions)
    correct_counts = np.zeros(n_transitions)
    n_halluc = sum(1 for r in results if r["is_hallucination"])
    n_correct = sum(1 for r in results if not r["is_hallucination"])

    for r in results:
        for pos in r.get("flip_positions", []):
            idx = pos - layer_start
            if 0 <= idx < n_transitions:
                if r["is_hallucination"]:
                    halluc_counts[idx] += 1
                else:
                    correct_counts[idx] += 1

    x = np.arange(n_transitions)
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x - width/2, halluc_counts / max(n_halluc, 1), width, label="Hallucination", color="red", alpha=0.7)
    ax.bar(x + width/2, correct_counts / max(n_correct, 1), width, label="Correct", color="green", alpha=0.7)

    ax.set_xlabel("Layer Transition")
    ax.set_ylabel("Flip Rate")
    ax.set_title("Flip Rate per Layer Transition")
    ax.set_xticks(x)
    ax.set_xticklabels([f"L{i}→L{i+1}" for i in range(layer_start, layer_end)])
    ax.legend()

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    return save_path
