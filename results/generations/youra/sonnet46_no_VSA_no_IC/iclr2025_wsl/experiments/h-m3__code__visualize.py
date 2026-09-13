"""Visualization for H-M3: 4 required figures."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ENCODER_COLORS = {
    "flat_mlp": "#E67E22",
    "flat_mlp_perm_aug": "#3498DB",
    "gnn_nfn": "#2ECC71",
}
ENCODER_LABELS = {
    "flat_mlp": "Flat-MLP",
    "flat_mlp_perm_aug": "Flat-MLP + PermAug",
    "gnn_nfn": "GNN-NFN (equivariant)",
}


def plot_gate_metrics(results: dict, out_path: str, zoo: str = "cifar10") -> None:
    """Bar chart: R² at N=100, 250 for all 3 encoders with bootstrap 95% CI error bars."""
    gate_sizes = [100, 250]
    encoders = ["flat_mlp", "flat_mlp_perm_aug", "gnn_nfn"]
    n_enc = len(encoders)
    n_sz = len(gate_sizes)

    fig, axes = plt.subplots(1, n_sz, figsize=(10, 5), sharey=False)
    if n_sz == 1:
        axes = [axes]

    for ax, sz in zip(axes, gate_sizes):
        sz_str = str(sz)
        means, errs_lo, errs_hi, colors, labels = [], [], [], [], []
        for enc in encoders:
            d = results.get(enc, {}).get(zoo, {}).get(sz_str, {})
            mean_r2 = d.get("mean_r2", 0.0)
            ci_lo = d.get("ci_lo", mean_r2)
            ci_hi = d.get("ci_hi", mean_r2)
            means.append(mean_r2)
            errs_lo.append(mean_r2 - ci_lo)
            errs_hi.append(ci_hi - mean_r2)
            colors.append(ENCODER_COLORS[enc])
            labels.append(ENCODER_LABELS[enc])

        x = np.arange(n_enc)
        bars = ax.bar(x, means, color=colors, alpha=0.85, width=0.6)
        ax.errorbar(x, means, yerr=[errs_lo, errs_hi], fmt="none", color="black",
                    capsize=5, linewidth=1.5)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=20, ha="right", fontsize=9)
        ax.set_ylabel("R²")
        ax.set_title(f"N={sz}")
        ax.axhline(0, color="gray", linewidth=0.8, linestyle="--")

    fig.suptitle("Gate Metrics: R² at N=100, 250 (bootstrap 95% CI)", fontsize=11)
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[H-M3] Saved: {out_path}")


def plot_ordering_curve(results: dict, out_path: str, zoo: str = "cifar10") -> None:
    """Line plot: R² vs N for all 3 conditions with CI bands."""
    encoders = ["flat_mlp", "flat_mlp_perm_aug", "gnn_nfn"]
    fig, ax = plt.subplots(figsize=(8, 5))

    for enc in encoders:
        data = results.get(enc, {}).get(zoo, {})
        sizes = sorted([int(k) for k in data if k != "full"])
        xs = sizes
        means = [data[str(s)]["mean_r2"] for s in sizes]
        lo = [data[str(s)]["ci_lo"] for s in sizes]
        hi = [data[str(s)]["ci_hi"] for s in sizes]

        color = ENCODER_COLORS[enc]
        ax.plot(xs, means, marker="o", color=color, label=ENCODER_LABELS[enc], linewidth=2)
        ax.fill_between(xs, lo, hi, color=color, alpha=0.2)

    ax.set_xlabel("Training size (N)")
    ax.set_ylabel("R²")
    ax.set_title("Sample Efficiency: R² vs Training Size (CIFAR-10)")
    ax.legend()
    ax.axhline(0, color="gray", linewidth=0.8, linestyle="--")
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[H-M3] Saved: {out_path}")


def plot_gap_fraction(gap_analysis: dict, out_path: str) -> None:
    """Bar chart: perm_aug_fraction at N=100, 250 with horizontal bands at 0.5 and 0.8."""
    gate_sizes = [100, 250]
    fractions = [gap_analysis.get(str(s), {}).get("perm_aug_fraction", 0.0) for s in gate_sizes]

    fig, ax = plt.subplots(figsize=(6, 5))
    colors = ["#3498DB" if f > 0 else "#E67E22" for f in fractions]
    ax.bar([str(s) for s in gate_sizes], fractions, color=colors, alpha=0.8, width=0.5)
    ax.axhline(0.5, color="green", linestyle="--", linewidth=1.5, label="50% (P2 lower)")
    ax.axhline(0.8, color="orange", linestyle="--", linewidth=1.5, label="80% (P2 upper)")
    ax.set_xlabel("Training size (N)")
    ax.set_ylabel("PermAug fraction of equivariant gap")
    ax.set_title("PermAug Gap Fraction\n(perm_aug−flat_mlp)/(gnn_nfn−flat_mlp)")
    ax.legend()
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[H-M3] Saved: {out_path}")


def plot_training_curves(train_curves: dict, out_path: str) -> None:
    """Line plot: training loss for flat_mlp vs flat_mlp_perm_aug at each N."""
    fig, ax = plt.subplots(figsize=(8, 5))

    for label, losses in train_curves.items():
        if losses:
            ax.plot(losses, label=label, linewidth=1.5)

    ax.set_xlabel("Epoch")
    ax.set_ylabel("MSE Loss")
    ax.set_title("Training Loss: Flat-MLP vs Flat-MLP + PermAug")
    ax.legend()
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[H-M3] Saved: {out_path}")
