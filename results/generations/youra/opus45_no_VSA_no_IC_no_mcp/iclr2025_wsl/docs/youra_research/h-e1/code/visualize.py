from typing import Dict, List
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import torch
from torch import Tensor
from sklearn.manifold import TSNE


def plot_accuracy_comparison(results: Dict, out_path: str) -> None:
    models = list(results.keys())
    accs = [results[m]["accuracy"] * 100 for m in models]

    plt.figure(figsize=(8, 5))
    bars = plt.bar(models, accs, color=["#4C72B0", "#55A868", "#C44E52"])
    plt.ylabel("Test Accuracy (%)")
    plt.title("Model Accuracy Comparison")
    plt.ylim(0, 100)

    for bar, acc in zip(bars, accs):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                 f"{acc:.1f}%", ha="center", va="bottom")

    plt.tight_layout()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_attention_heatmap(attn_weights: Tensor, out_path: str) -> None:
    attn = attn_weights[0, 0].cpu().numpy()

    plt.figure(figsize=(6, 5))
    plt.imshow(attn, cmap="viridis", aspect="auto")
    plt.colorbar(label="Attention Weight")
    plt.xlabel("Key Position (Layer)")
    plt.ylabel("Query Position (Layer)")
    plt.title("NFT Attention Pattern (Head 0, Sample 0)")

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_layer_activation_profile(layer_acts: List[Tensor], out_path: str) -> None:
    variances = [feat.var(dim=0).mean().item() for feat in layer_acts]

    plt.figure(figsize=(8, 5))
    plt.bar(range(len(variances)), variances, color="#55A868")
    plt.xlabel("Layer Index")
    plt.ylabel("Activation Variance")
    plt.title("DWS Per-Layer Activation Variance")

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_tsne_representations(
    dws_reprs: Tensor,
    nft_reprs: Tensor,
    labels: Tensor,
    out_path: str
) -> None:
    dws_np = dws_reprs.cpu().numpy()
    nft_np = nft_reprs.cpu().numpy()
    labels_np = labels.cpu().numpy()

    tsne = TSNE(n_components=2, random_state=42, perplexity=min(30, len(labels_np) - 1))

    combined = np.vstack([dws_np, nft_np])
    embedded = tsne.fit_transform(combined)

    n = len(dws_np)
    dws_emb = embedded[:n]
    nft_emb = embedded[n:]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    scatter1 = axes[0].scatter(dws_emb[:, 0], dws_emb[:, 1], c=labels_np, cmap="tab10", alpha=0.7)
    axes[0].set_title("DWS Representations")
    axes[0].set_xlabel("t-SNE 1")
    axes[0].set_ylabel("t-SNE 2")

    scatter2 = axes[1].scatter(nft_emb[:, 0], nft_emb[:, 1], c=labels_np, cmap="tab10", alpha=0.7)
    axes[1].set_title("NFT Representations")
    axes[1].set_xlabel("t-SNE 1")
    axes[1].set_ylabel("t-SNE 2")

    plt.colorbar(scatter2, ax=axes[1], label="Digit Class")

    plt.tight_layout()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
