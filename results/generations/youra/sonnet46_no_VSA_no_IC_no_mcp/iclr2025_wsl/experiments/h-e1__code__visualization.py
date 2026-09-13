import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def _ensure_dir(out_dir):
    os.makedirs(out_dir, exist_ok=True)


def fig_gate_metrics(stats, out_dir="docs/youra_research/h-e1/figures"):
    _ensure_dir(out_dir)
    sym_types = [k for k in stats if not k.startswith("_")]
    means = [stats[s]["mean"] for s in sym_types]
    ci_lo = [stats[s]["mean"] - stats[s]["ci_lower"] for s in sym_types]
    ci_hi = [stats[s]["ci_upper"] - stats[s]["mean"] for s in sym_types]

    fig, ax = plt.subplots(figsize=(7, 4))
    x = range(len(sym_types))
    ax.bar(x, means, yerr=[ci_lo, ci_hi], capsize=5, color=["steelblue", "salmon", "mediumseagreen"])
    ax.axhline(0.05, color="red", linestyle="--", label="threshold=0.05")
    ax.set_xticks(list(x))
    ax.set_xticklabels(sym_types)
    ax.set_ylabel("Mean cosine distance")
    ax.set_title("Gate metric: mean cosine distance per symmetry type")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "fig_gate_metrics.png"), dpi=150)
    plt.close(fig)


def fig_orbit_distribution(distances, out_dir="docs/youra_research/h-e1/figures"):
    _ensure_dir(out_dir)
    fig, ax = plt.subplots(figsize=(8, 4))
    colors = {"scaling": "steelblue", "signflip": "salmon", "combined": "mediumseagreen"}
    for sym_type, data in distances.items():
        if sym_type.startswith("_"):
            continue
        ax.hist(data["cosine"], bins=50, alpha=0.6, label=sym_type, color=colors.get(sym_type))
    ax.axvline(0.05, color="red", linestyle="--", label="threshold=0.05")
    ax.set_xlabel("Cosine distance")
    ax.set_ylabel("Count")
    ax.set_title("Distribution of orbit cosine distances")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "fig_orbit_distribution.png"), dpi=150)
    plt.close(fig)


def fig_l2_vs_cosine(distances, out_dir="docs/youra_research/h-e1/figures"):
    _ensure_dir(out_dir)
    fig, ax = plt.subplots(figsize=(7, 5))
    colors = {"scaling": "steelblue", "signflip": "salmon", "combined": "mediumseagreen"}
    for sym_type, data in distances.items():
        if sym_type.startswith("_"):
            continue
        ax.scatter(data["cosine"], data["l2"], alpha=0.3, s=5,
                   label=sym_type, color=colors.get(sym_type))
    ax.set_xlabel("Cosine distance")
    ax.set_ylabel("L2 distance")
    ax.set_title("L2 vs cosine distance by symmetry type")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "fig_l2_vs_cosine.png"), dpi=150)
    plt.close(fig)


def fig_scale_vs_diameter(distances, out_dir="docs/youra_research/h-e1/figures"):
    _ensure_dir(out_dir)
    if "scaling" not in distances or "max_scale" not in distances["scaling"]:
        return
    ms = distances["scaling"]["max_scale"]
    cd = distances["scaling"]["cosine"]
    # max_scale is per-model (N), cosine is per model*K (N*K); repeat each N value K times
    N = len(ms)
    total = len(cd)
    K = total // N
    ms_rep = np.repeat(ms, K)
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(ms_rep, cd, alpha=0.3, s=5, color="steelblue")
    ax.set_xlabel("max_scale (max(α, 1/α))")
    ax.set_ylabel("Cosine distance")
    ax.set_title("Scale magnitude vs orbit diameter (scaling symmetry)")
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "fig_scale_vs_diameter.png"), dpi=150)
    plt.close(fig)
