import os
from typing import Dict, List
import numpy as np
import matplotlib.pyplot as plt


def plot_gradient_heatmap(dws_grads: Dict[str, List[float]], nft_grads: Dict[str, List[float]], out_path: str) -> None:
    """Plot per-layer gradient magnitudes over training (DWS vs NFT side-by-side)."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    for ax, (name, grads) in zip(axes, [("DWS", dws_grads), ("NFT", nft_grads)]):
        if not grads:
            ax.set_title(f"{name} - No data")
            continue
        layers = list(grads.keys())
        data = np.array([grads[l] for l in layers])
        if data.size == 0:
            continue
        im = ax.imshow(data, aspect="auto", cmap="viridis")
        ax.set_xlabel("Epoch")
        ax.set_ylabel("Layer")
        ax.set_title(f"{name} Gradient Norms")
        ax.set_yticks(range(len(layers)))
        ax.set_yticklabels([l.split(".")[-1][:10] for l in layers], fontsize=6)
        plt.colorbar(im, ax=ax)

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_locality_evolution(dws_updates: Dict[str, List[float]], out_path: str) -> None:
    """Plot DWS locality score evolution over training."""
    if not dws_updates:
        return
    snapshots = max(len(v) for v in dws_updates.values())
    locality_scores = []
    for i in range(snapshots):
        updates_at_i = [v[i] for v in dws_updates.values() if len(v) > i]
        if updates_at_i:
            mean = np.mean(updates_at_i)
            score = np.std(updates_at_i) / mean * 100 if mean > 1e-10 else 0
            locality_scores.append(score)

    plt.figure(figsize=(8, 5))
    plt.plot(range(1, len(locality_scores) + 1), locality_scores, "b-o", linewidth=2)
    plt.xlabel("Snapshot")
    plt.ylabel("Locality Score (CoV * 100)")
    plt.title("DWS Locality Score Evolution")
    plt.grid(True, alpha=0.3)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_attention_entropy_curve(nft_entropy: List[float], out_path: str) -> None:
    """Plot NFT attention entropy over training epochs."""
    if not nft_entropy:
        return
    plt.figure(figsize=(8, 5))
    plt.plot(range(1, len(nft_entropy) + 1), nft_entropy, "r-o", linewidth=2)
    plt.xlabel("Epoch")
    plt.ylabel("Attention Entropy")
    plt.title("NFT Attention Entropy Evolution")
    plt.grid(True, alpha=0.3)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_layerwise_update_boxplot(dws_updates: Dict, nft_updates: Dict, out_path: str) -> None:
    """Box plots comparing weight update magnitudes across layers."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    for ax, (name, updates) in zip(axes, [("DWS", dws_updates), ("NFT", nft_updates)]):
        if not updates:
            ax.set_title(f"{name} - No data")
            continue
        data = [updates[l] for l in updates.keys()]
        labels = [l.split(".")[-1][:8] for l in updates.keys()]
        ax.boxplot(data, labels=labels)
        ax.set_xlabel("Layer")
        ax.set_ylabel("Weight Update Magnitude")
        ax.set_title(f"{name} Layer-wise Updates")
        ax.tick_params(axis="x", rotation=45)

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_gate_metrics(results: Dict, success_results: Dict, out_path: str) -> None:
    """Required gate figure: training dynamics metrics comparison."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # 1. Wasserstein distance bar
    ax = axes[0, 0]
    w_dist = success_results.get("wasserstein_distance", 0)
    threshold = 0.1
    ax.bar(["Measured", "Threshold"], [w_dist, threshold], color=["blue", "red"], alpha=0.7)
    ax.set_ylabel("Wasserstein Distance")
    ax.set_title(f"Gradient Flow Difference: {'PASS' if w_dist > threshold else 'FAIL'}")

    # 2. CoV comparison
    ax = axes[0, 1]
    dws_cov = success_results.get("dws_cov", 0)
    nft_cov = success_results.get("nft_cov", 0)
    ax.bar(["DWS", "NFT"], [dws_cov, nft_cov], color=["green", "orange"], alpha=0.7)
    ax.set_ylabel("Coefficient of Variation")
    ax.set_title(f"Weight Update Localization: {'PASS' if dws_cov > nft_cov else 'FAIL'}")

    # 3. NFT entropy evolution
    ax = axes[1, 0]
    nft_data = results.get("nft", [{}])[0]
    entropy = nft_data.get("attention_entropy", [])
    if entropy:
        ax.plot(entropy, "r-", linewidth=2)
        ax.set_xlabel("Epoch")
        ax.set_ylabel("Attention Entropy")
    ax.set_title(f"NFT Attention Entropy: {'PASS' if success_results.get('nft_entropy_increases') else 'FAIL'}")

    # 4. Summary
    ax = axes[1, 1]
    ax.axis("off")
    summary = [
        f"Gradient Flow Different: {success_results.get('gradient_flow_different')}",
        f"DWS More Localized: {success_results.get('dws_more_localized')}",
        f"NFT Entropy Increases: {success_results.get('nft_entropy_increases')}",
        f"Early Signature: {success_results.get('early_signature_detected')}",
        "",
        f"OVERALL: {'PASS' if success_results.get('all_criteria_pass') else 'FAIL'}"
    ]
    ax.text(0.1, 0.5, "\n".join(summary), fontsize=12, family="monospace", verticalalignment="center")

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()
