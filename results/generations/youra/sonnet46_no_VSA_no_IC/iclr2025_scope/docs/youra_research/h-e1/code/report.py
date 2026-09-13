"""Reporting and figures for h-e1."""
import json
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import spearmanr


def compute_spearman(entropy_A, entropy_B, entropy_C, gate_threshold=0.8):
    """
    Compute 3 pairwise Spearman rank correlations.

    Returns:
        dict with rho_AB, rho_AC, rho_BC, p values, min_rho, mean_rho, gate_pass
    """
    rho_AB, p_AB = spearmanr(entropy_A, entropy_B)
    rho_AC, p_AC = spearmanr(entropy_A, entropy_C)
    rho_BC, p_BC = spearmanr(entropy_B, entropy_C)

    min_rho = min(rho_AB, rho_AC, rho_BC)
    mean_rho = (rho_AB + rho_AC + rho_BC) / 3.0

    return {
        "rho_AB": float(rho_AB),
        "p_AB": float(p_AB),
        "rho_AC": float(rho_AC),
        "p_AC": float(p_AC),
        "rho_BC": float(rho_BC),
        "p_BC": float(p_BC),
        "min_rho": float(min_rho),
        "mean_rho": float(mean_rho),
        "gate_pass": bool(min_rho >= gate_threshold),
        "gate_threshold": gate_threshold,
    }


def save_results_json(spearman, entropy_A, entropy_B, entropy_C, out_path="results.json"):
    """Save full results to JSON."""
    results = {
        "hypothesis": "h-e1",
        "experiment": "per-layer attention entropy stability",
        "dataset": "Salesforce/wikitext wikitext-103-raw-v1 validation",
        "model": "meta-llama/Llama-2-7b-hf",
        "n_subsets": 3,
        "subset_size": 100,
        "seqlen": 2048,
        "gate": {
            "type": "MUST_WORK",
            "criterion": "min(rho_AB, rho_AC, rho_BC) >= 0.8",
            "result": "PASS" if spearman["gate_pass"] else "FAIL",
        },
        "metrics": spearman,
        "entropy_per_layer": {
            "subset_A": entropy_A.tolist(),
            "subset_B": entropy_B.tolist(),
            "subset_C": entropy_C.tolist(),
        },
        "top8_layers": {
            "subset_A": np.argsort(entropy_A)[::-1][:8].tolist(),
            "subset_B": np.argsort(entropy_B)[::-1][:8].tolist(),
            "subset_C": np.argsort(entropy_C)[::-1][:8].tolist(),
        },
    }
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved: {out_path}")


def generate_figures(spearman, entropy_A, entropy_B, entropy_C, figures_dir="figures/"):
    """Generate and save 4 figures."""
    pathlib.Path(figures_dir).mkdir(parents=True, exist_ok=True)
    threshold = spearman["gate_threshold"]

    # Figure 1: entropy_stability.png
    rho_vals = [spearman["rho_AB"], spearman["rho_AC"], spearman["rho_BC"]]
    colors = ["green" if r >= threshold else "red" for r in rho_vals]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(["ρ(A,B)", "ρ(A,C)", "ρ(B,C)"], rho_vals, color=colors)
    ax.axhline(threshold, color="black", linestyle="--", label=f"threshold={threshold}")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Spearman ρ")
    ax.set_title(f"Entropy Stability — Gate: {'PASS' if spearman['gate_pass'] else 'FAIL'}")
    ax.legend()
    fig.savefig(f"{figures_dir}/entropy_stability.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # Figure 2: layer_entropy_per_subset.png
    layers = np.arange(len(entropy_A))
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(layers, entropy_A, label="Subset A", alpha=0.8)
    ax.plot(layers, entropy_B, label="Subset B", alpha=0.8)
    ax.plot(layers, entropy_C, label="Subset C", alpha=0.8)
    ax.set_xlabel("Layer Index")
    ax.set_ylabel("Mean Entropy")
    ax.set_title("Per-Layer Attention Entropy (3 Subsets)")
    ax.legend()
    fig.savefig(f"{figures_dir}/layer_entropy_per_subset.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # Figure 3: rank_correlation_scatter.png
    pairs = [
        ("A", "B", entropy_A, entropy_B, spearman["rho_AB"]),
        ("A", "C", entropy_A, entropy_C, spearman["rho_AC"]),
        ("B", "C", entropy_B, entropy_C, spearman["rho_BC"]),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for ax, (la, lb, ea, eb, rho) in zip(axes, pairs):
        ax.scatter(ea, eb, alpha=0.7)
        ax.set_xlabel(f"Entropy {la}")
        ax.set_ylabel(f"Entropy {lb}")
        ax.set_title(f"ρ={rho:.3f}")
    fig.tight_layout()
    fig.savefig(f"{figures_dir}/rank_correlation_scatter.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # Figure 4: top8_overlap.png
    top8_A = set(np.argsort(entropy_A)[::-1][:8].tolist())
    top8_B = set(np.argsort(entropy_B)[::-1][:8].tolist())
    top8_C = set(np.argsort(entropy_C)[::-1][:8].tolist())
    overlap_ABC = top8_A & top8_B & top8_C
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.axis("off")
    table_data = [
        ["Subset A top-8", str(sorted(top8_A))],
        ["Subset B top-8", str(sorted(top8_B))],
        ["Subset C top-8", str(sorted(top8_C))],
        ["3-way overlap", str(sorted(overlap_ABC))],
        ["|overlap|", str(len(overlap_ABC))],
    ]
    ax.table(cellText=table_data, colLabels=["Metric", "Value"], loc="center", cellLoc="left")
    ax.set_title("Top-8 Highest-Entropy Layer Overlap")
    fig.savefig(f"{figures_dir}/top8_overlap.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    print(f"Figures saved to {figures_dir}")
