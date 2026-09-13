import os
from typing import Dict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def plot_cosine_similarity_bar(
    results: Dict[str, float],
    model_name: str,
    output_path: str,
    threshold: float = 0.95,
) -> None:
    """Bar chart of per-layer cosine similarity with threshold line."""
    if not results:
        return

    # Sort keys for consistent ordering
    keys = sorted(results.keys())
    # Shorten labels: keep layer index and lora_A/lora_B
    labels = []
    for k in keys:
        parts = k.split(".")
        layer_parts = [p for p in parts if p.isdigit() or "lora" in p.lower()]
        labels.append(".".join(layer_parts) if layer_parts else k[-30:])

    values = [results[k] for k in keys]

    fig, ax = plt.subplots(figsize=(max(10, len(keys) * 0.4), 6))
    colors = ["#d62728" if v < threshold else "#1f77b4" for v in values]
    bars = ax.bar(range(len(keys)), values, color=colors, alpha=0.8)

    ax.axhline(y=threshold, color="red", linestyle="--", linewidth=1.5,
               label=f"Threshold = {threshold}")
    ax.set_xlabel("LoRA Layer")
    ax.set_ylabel("Cosine Similarity")
    ax.set_title(f"Per-Layer LoRA Cosine Similarity: {model_name}")
    ax.set_xticks(range(len(keys)))
    ax.set_xticklabels(labels, rotation=90, fontsize=7)
    ax.set_ylim(0, 1.05)
    ax.legend()

    below = sum(1 for v in values if v < threshold)
    ax.text(0.02, 0.02,
            f"Layers below threshold: {below}/{len(values)}\nMin: {min(values):.4f}  Mean: {sum(values)/len(values):.4f}",
            transform=ax.transAxes, fontsize=9,
            verticalalignment="bottom",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def generate_all_figures(
    llama2_results: Dict[str, float],
    mistral_results: Dict[str, float],
    figures_dir: str,
) -> None:
    os.makedirs(figures_dir, exist_ok=True)
    plot_cosine_similarity_bar(
        llama2_results,
        model_name="LLaMA-2-7B",
        output_path=os.path.join(figures_dir, "cosine_similarity_bar_llama2.png"),
    )
    plot_cosine_similarity_bar(
        mistral_results,
        model_name="Mistral-7B-v0.1",
        output_path=os.path.join(figures_dir, "cosine_similarity_bar_mistral.png"),
    )
