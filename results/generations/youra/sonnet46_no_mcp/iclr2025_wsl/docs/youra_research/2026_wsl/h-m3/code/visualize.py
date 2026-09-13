import logging
from pathlib import Path
from typing import Dict, Tuple, Optional

import numpy as np

logger = logging.getLogger(__name__)

ENCODER_COLORS = {
    "FlatMLP":  "#4C72B0",
    "DeepSets": "#DD8452",
    "NFN":      "#55A868",
}
STYLE = "seaborn-v0_8-whitegrid"


def _setup_style():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as _plt
    try:
        _plt.style.use(STYLE)
    except Exception:
        _plt.style.use("seaborn-whitegrid")
    return _plt


def plot_rho_comparison(results: Dict, figures_dir: Path) -> None:
    """Bar chart: rho per encoder per zoo with 95% CI error bars."""
    plt = _setup_style()

    enc = results.get("encoders", {})
    encoders = ["flat_mlp", "deep_sets", "nfn"]
    labels_enc = ["FlatMLP", "DeepSets", "NFN"]
    zoos = ["mnist_cnn", "cifar10"]
    zoo_labels = ["MNIST-CNN", "CIFAR-10"]
    colors = [ENCODER_COLORS[l] for l in labels_enc]

    fig, axes = plt.subplots(1, 2, figsize=(10, 6))
    for ax, zoo, zoo_label in zip(axes, zoos, zoo_labels):
        rhos, yerr_low, yerr_high = [], [], []
        for e in encoders:
            d = enc.get(e, {}).get(zoo, {})
            rho = d.get("rho", float("nan"))
            ci_l = d.get("ci_lower", float("nan"))
            ci_u = d.get("ci_upper", float("nan"))
            rhos.append(rho if not np.isnan(rho) else 0)
            yerr_low.append(max(rho - ci_l, 0) if not np.isnan(ci_l) else 0)
            yerr_high.append(max(ci_u - rho, 0) if not np.isnan(ci_u) else 0)

        x = np.arange(len(encoders))
        bars = ax.bar(x, rhos, color=colors, yerr=[yerr_low, yerr_high],
                      capsize=5, alpha=0.85)
        ax.axhline(y=0.05, color="red", linestyle="--", alpha=0.5, label="threshold=0.05")
        ax.set_xticks(x)
        ax.set_xticklabels(labels_enc)
        ax.set_ylabel("Spearman ρ")
        ax.set_title(f"{zoo_label}")
        ax.set_ylim(bottom=min(0, min(r - e for r, e in zip(rhos, yerr_low)) - 0.05))

        # Annotate delta_rho
        dm = results.get("delta_metrics", {})
        key = "delta_rho_mnist" if zoo == "mnist_cnn" else "delta_rho_cifar"
        dr = dm.get(key)
        if dr is not None and not np.isnan(dr):
            ax.annotate(f"Δρ={dr:.3f}", xy=(2, rhos[2]), xytext=(1.5, rhos[2] + 0.05),
                        arrowprops=dict(arrowstyle="->"), fontsize=9)

    fig.suptitle("Spearman ρ Comparison: FlatMLP vs DeepSets vs NFN")
    plt.tight_layout()
    out = Path(figures_dir) / "rho_comparison.png"
    plt.savefig(out, dpi=150)
    plt.close()
    logger.info(f"Saved {out}")


def plot_symmetry_spectrum(results: Dict, figures_dir: Path) -> None:
    """Scatter: rho vs symmetry level on MNIST-CNN."""
    plt = _setup_style()

    enc = results.get("encoders", {})
    sym_levels = {"flat_mlp": 0, "deep_sets": 1, "nfn": 2}
    sym_labels = {0: "None\n(FlatMLP)", 1: "Invariant\n(DeepSets)", 2: "Equivariant\n(NFN)"}
    colors = {"flat_mlp": ENCODER_COLORS["FlatMLP"],
              "deep_sets": ENCODER_COLORS["DeepSets"],
              "nfn": ENCODER_COLORS["NFN"]}

    fig, ax = plt.subplots(figsize=(7, 5))
    for e, sym in sym_levels.items():
        d = enc.get(e, {}).get("mnist_cnn", {})
        rho = d.get("rho", float("nan"))
        n_params = d.get("param_count", 500_000)
        if not np.isnan(rho):
            ax.scatter(sym, rho, s=n_params / 1000, color=colors[e], alpha=0.8,
                       label=e.replace("_", " ").title(), zorder=3)
            ax.annotate(f"ρ={rho:.3f}", (sym, rho), textcoords="offset points",
                        xytext=(5, 5), fontsize=9)

    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels([sym_labels[i] for i in range(3)])
    ax.set_ylabel("Spearman ρ (MNIST-CNN)")
    ax.set_title("Symmetry Level vs Predictive Accuracy")
    ax.legend()
    plt.tight_layout()
    out = Path(figures_dir) / "symmetry_spectrum.png"
    plt.savefig(out, dpi=150)
    plt.close()
    logger.info(f"Saved {out}")


def plot_tier_delta_rho(tier_results: Dict, figures_dir: Path) -> None:
    """Bar chart: delta_rho(NFN vs flat) per accuracy tercile."""
    plt = _setup_style()

    tiers = ["low", "mid", "high"]
    values = [tier_results.get(t, float("nan")) for t in tiers]
    ns = [tier_results.get(f"{t}_n", 0) for t in tiers]

    fig, ax = plt.subplots(figsize=(7, 5))
    colors = ["#4C72B0", "#DD8452", "#55A868"]
    bars = ax.bar(tiers, [v if not np.isnan(v) else 0 for v in values],
                  color=colors, alpha=0.85)
    ax.axhline(y=0, color="black", linewidth=0.8)
    for bar, n in zip(bars, ns):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.002,
                f"n={n}", ha="center", va="bottom", fontsize=9)
    ax.set_xlabel("Accuracy Tercile")
    ax.set_ylabel("Δρ (NFN − FlatMLP)")
    ax.set_title("NFN vs FlatMLP Δρ per Accuracy Tier (MNIST-CNN)")
    plt.tight_layout()
    out = Path(figures_dir) / "tier_delta_rho.png"
    plt.savefig(out, dpi=150)
    plt.close()
    logger.info(f"Saved {out}")


def plot_bootstrap_distribution(boot_deltas: np.ndarray, ci: Tuple,
                                 figures_dir: Path) -> None:
    """Histogram of bootstrap delta_rho distribution with CI shading."""
    plt = _setup_style()
    delta_rho, ci_lower, ci_upper = ci

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(boot_deltas, bins=50, color="#4C72B0", alpha=0.7, edgecolor="white")
    ax.axvspan(ci_lower, ci_upper, alpha=0.2, color="#55A868", label=f"95% CI [{ci_lower:.3f}, {ci_upper:.3f}]")
    ax.axvline(delta_rho, color="red", linewidth=2, label=f"Point estimate Δρ={delta_rho:.3f}")
    ax.axvline(0, color="black", linewidth=1, linestyle="--", label="Δρ=0")
    ax.set_xlabel("Bootstrap Δρ (NFN − FlatMLP)")
    ax.set_ylabel("Count")
    ax.set_title("Bootstrap Distribution of Δρ (MNIST-CNN)")
    ax.legend()
    plt.tight_layout()
    out = Path(figures_dir) / "bootstrap_dist.png"
    plt.savefig(out, dpi=150)
    plt.close()
    logger.info(f"Saved {out}")


def plot_cross_zoo_consistency(results: Dict, figures_dir: Path) -> None:
    """Side-by-side rho bars: MNIST-CNN vs CIFAR-10 for all three encoders."""
    plt = _setup_style()

    enc = results.get("encoders", {})
    encoders = ["flat_mlp", "deep_sets", "nfn"]
    labels_enc = ["FlatMLP", "DeepSets", "NFN"]
    colors = [ENCODER_COLORS[l] for l in labels_enc]

    mnist_rhos = [enc.get(e, {}).get("mnist_cnn", {}).get("rho", float("nan")) for e in encoders]
    cifar_rhos = [enc.get(e, {}).get("cifar10", {}).get("rho", float("nan")) for e in encoders]

    x = np.arange(len(encoders))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 5))
    bars1 = ax.bar(x - width/2, [r if not np.isnan(r) else 0 for r in mnist_rhos],
                   width, label="MNIST-CNN", color=colors, alpha=0.85)
    bars2 = ax.bar(x + width/2, [r if not np.isnan(r) else 0 for r in cifar_rhos],
                   width, label="CIFAR-10", color=colors, alpha=0.5, hatch="//")

    ax.set_xticks(x)
    ax.set_xticklabels(labels_enc)
    ax.set_ylabel("Spearman ρ")
    ax.set_title("Cross-Zoo Consistency: MNIST-CNN vs CIFAR-10")
    ax.legend()
    plt.tight_layout()
    out = Path(figures_dir) / "cross_zoo.png"
    plt.savefig(out, dpi=150)
    plt.close()
    logger.info(f"Saved {out}")
