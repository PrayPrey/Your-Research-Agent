"""Visualizations for H-M1."""
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import torch
import os


def plot_gate_comparison(bert_metrics: dict, gpt2_metrics: dict, out_path: str) -> None:
    """Bar chart comparing BERT vs GPT-2 upper triangle sparsity."""
    plt.figure(figsize=(8, 6))

    models = ["BERT", "GPT-2"]
    sparsities = [bert_metrics["upper_sparsity"], gpt2_metrics["upper_sparsity"]]
    colors = ["#3498db", "#e74c3c"]

    bars = plt.bar(models, sparsities, color=colors, edgecolor="black", linewidth=1.5)

    # Add threshold lines
    plt.axhline(y=0.10, color="blue", linestyle="--", label="BERT threshold (<0.10)")
    plt.axhline(y=0.99, color="red", linestyle="--", label="GPT-2 threshold (>0.99)")

    plt.ylabel("Upper Triangle Sparsity", fontsize=12)
    plt.title("Attention Pattern Sparsity: BERT vs GPT-2", fontsize=14)
    plt.ylim(0, 1.05)
    plt.legend(loc="upper left")

    # Add value labels
    for bar, val in zip(bars, sparsities):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                 f"{val:.4f}", ha="center", fontsize=11)

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_attention_heatmaps(
    bert_attn: torch.Tensor,
    gpt2_attn: torch.Tensor,
    tokens_bert: list[str],
    tokens_gpt2: list[str],
    out_path: str,
) -> None:
    """Plot attention heatmaps for first layer, first head."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # BERT heatmap (first layer, first head)
    bert_map = bert_attn[0, 0].numpy()  # [S, S]
    ax1 = axes[0]
    sns.heatmap(bert_map, ax=ax1, cmap="Blues", vmin=0, vmax=1,
                xticklabels=tokens_bert[:len(bert_map)],
                yticklabels=tokens_bert[:len(bert_map)])
    ax1.set_title("BERT Attention (Layer 0, Head 0)")
    ax1.set_xlabel("Key")
    ax1.set_ylabel("Query")

    # GPT-2 heatmap
    gpt2_map = gpt2_attn[0, 0].numpy()
    ax2 = axes[1]
    sns.heatmap(gpt2_map, ax=ax2, cmap="Reds", vmin=0, vmax=1,
                xticklabels=tokens_gpt2[:len(gpt2_map)],
                yticklabels=tokens_gpt2[:len(gpt2_map)])
    ax2.set_title("GPT-2 Attention (Layer 0, Head 0)")
    ax2.set_xlabel("Key")
    ax2.set_ylabel("Query")

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_layerwise_sparsity(
    bert_layers: list[float],
    gpt2_layers: list[float],
    out_path: str,
) -> None:
    """Line plot of per-layer upper triangle sparsity."""
    plt.figure(figsize=(10, 6))

    layers = list(range(len(bert_layers)))
    plt.plot(layers, bert_layers, "b-o", label="BERT", linewidth=2, markersize=8)
    plt.plot(layers, gpt2_layers, "r-s", label="GPT-2", linewidth=2, markersize=8)

    plt.xlabel("Layer", fontsize=12)
    plt.ylabel("Upper Triangle Sparsity", fontsize=12)
    plt.title("Per-Layer Attention Sparsity", fontsize=14)
    plt.legend(fontsize=11)
    plt.xticks(layers)
    plt.ylim(0, 1.05)
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_entropy_histogram(
    bert_entropy: torch.Tensor,
    gpt2_entropy: torch.Tensor,
    out_path: str,
) -> None:
    """Histogram of per-head entropy values."""
    plt.figure(figsize=(10, 6))

    bert_vals = bert_entropy.flatten().numpy()
    gpt2_vals = gpt2_entropy.flatten().numpy()

    plt.hist(bert_vals, bins=30, alpha=0.6, label="BERT", color="blue")
    plt.hist(gpt2_vals, bins=30, alpha=0.6, label="GPT-2", color="red")

    plt.xlabel("Attention Entropy", fontsize=12)
    plt.ylabel("Count", fontsize=12)
    plt.title("Distribution of Per-Head Attention Entropy", fontsize=14)
    plt.legend(fontsize=11)

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()
