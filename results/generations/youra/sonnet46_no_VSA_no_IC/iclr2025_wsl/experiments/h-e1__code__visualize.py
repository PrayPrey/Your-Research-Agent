"""Figure generation for H-E1 experiment results."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import config

ENCODER_LABELS = {
    "flat_mlp": "Flat-MLP",
    "flat_mlp_perm_aug": "Flat-MLP+PermAug",
    "nfn": "NFN (Equivariant)",
    "gnn_nfn": "GNN-NFN (Equivariant)",
}
COLORS = {
    "flat_mlp": "#4878CF",
    "flat_mlp_perm_aug": "#6ACC65",
    "nfn": "#D65F5F",
    "gnn_nfn": "#B47CC7",
}


def generate_all_figures(results: dict) -> list:
    """Generate all 4 figures, return list of saved paths."""
    os.makedirs(config.FIGURES_DIR, exist_ok=True)
    paths = []
    paths += generate_figure1_bar(results)
    paths += generate_figure2_learning_curves(results)
    paths += generate_figure3_ci_overlap(results)
    paths += generate_figure4_diversity(results)
    return paths


def generate_figure1_bar(results: dict) -> list:
    """Figure 1: R² bar chart at training_size=500, all conditions, per zoo."""
    budget_tier = "medium"
    size = 500
    zoo_names = [z for z in config.ZOO_NAMES if f"{z}_test_accuracies" in results]
    if not zoo_names:
        zoo_names = config.ZOO_NAMES

    n_zoos = len(zoo_names)
    fig, axes = plt.subplots(1, n_zoos, figsize=(6 * n_zoos, 5))
    if n_zoos == 1:
        axes = [axes]

    for ax, zoo in zip(axes, zoo_names):
        r2s, ci_errs = [], []
        labels = []
        for enc in config.ENCODER_NAMES:
            key = f"{zoo}_{enc}_{budget_tier}_{size}"
            r = results.get(key, {})
            r2 = r.get("r2", 0)
            ci_low = r.get("ci_low", r2)
            ci_high = r.get("ci_high", r2)
            r2s.append(r2)
            ci_errs.append([r2 - ci_low, ci_high - r2])
            labels.append(ENCODER_LABELS.get(enc, enc))

        x = np.arange(len(labels))
        yerr = np.array(ci_errs).T
        bars = ax.bar(x, r2s, yerr=yerr, capsize=5,
                      color=[COLORS.get(enc, "gray") for enc in config.ENCODER_NAMES],
                      alpha=0.85, ecolor="black", error_kw={"lw": 1.5})
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=20, ha="right", fontsize=9)
        ax.set_ylabel("R²", fontsize=11)
        ax.set_title(f"{zoo.upper()} Zoo — Training size=500", fontsize=11)
        ax.axhline(0, color="black", linewidth=0.5)
        ax.set_ylim(bottom=min(0, min(r2s) - 0.1))

    plt.tight_layout()
    path = os.path.join(config.FIGURES_DIR, "fig1_r2_bar_size500.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Figure 1 saved: {path}")
    return [path]


def generate_figure2_learning_curves(results: dict) -> list:
    """Figure 2: R² vs training size, all conditions, both zoos."""
    budget_tier = "medium"
    n_zoos = len(config.ZOO_NAMES)
    fig, axes = plt.subplots(1, n_zoos, figsize=(7 * n_zoos, 5))
    if n_zoos == 1:
        axes = [axes]

    x_labels = [str(s) for s in config.TRAINING_SIZES]
    x = np.arange(len(x_labels))

    for ax, zoo in zip(axes, config.ZOO_NAMES):
        for enc in config.ENCODER_NAMES:
            r2s = []
            for size in config.TRAINING_SIZES:
                key = f"{zoo}_{enc}_{budget_tier}_{size}"
                r2s.append(results.get(key, {}).get("r2", float("nan")))
            ax.plot(x, r2s, marker="o", label=ENCODER_LABELS.get(enc, enc),
                    color=COLORS.get(enc, "gray"), linewidth=2, markersize=6)

        ax.set_xticks(x)
        ax.set_xticklabels(x_labels)
        ax.set_xlabel("Training set size", fontsize=11)
        ax.set_ylabel("R²", fontsize=11)
        ax.set_title(f"{zoo.upper()} Zoo — Learning Curves", fontsize=11)
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    path = os.path.join(config.FIGURES_DIR, "fig2_learning_curves.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Figure 2 saved: {path}")
    return [path]


def generate_figure3_ci_overlap(results: dict) -> list:
    """Figure 3: CI band overlap plot — equivariant vs Flat-MLP per training size."""
    budget_tier = "medium"
    n_zoos = len(config.ZOO_NAMES)
    fig, axes = plt.subplots(1, n_zoos, figsize=(7 * n_zoos, 5))
    if n_zoos == 1:
        axes = [axes]

    x_labels = [str(s) for s in config.TRAINING_SIZES]
    x = np.arange(len(x_labels))
    compare_encoders = ["flat_mlp", "nfn", "gnn_nfn"]

    for ax, zoo in zip(axes, config.ZOO_NAMES):
        for enc in compare_encoders:
            r2s, lows, highs = [], [], []
            for size in config.TRAINING_SIZES:
                key = f"{zoo}_{enc}_{budget_tier}_{size}"
                r = results.get(key, {})
                r2s.append(r.get("r2", float("nan")))
                lows.append(r.get("ci_low", float("nan")))
                highs.append(r.get("ci_high", float("nan")))
            color = COLORS.get(enc, "gray")
            ax.plot(x, r2s, marker="o", color=color,
                    label=ENCODER_LABELS.get(enc, enc), linewidth=2)
            ax.fill_between(x, lows, highs, color=color, alpha=0.2)

        ax.set_xticks(x)
        ax.set_xticklabels(x_labels)
        ax.set_xlabel("Training size", fontsize=11)
        ax.set_ylabel("R² with 95% CI", fontsize=11)
        ax.set_title(f"{zoo.upper()} — CI Overlap (Equivariant vs Flat-MLP)", fontsize=11)
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    path = os.path.join(config.FIGURES_DIR, "fig3_ci_overlap.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Figure 3 saved: {path}")
    return [path]


def generate_figure4_diversity(results: dict) -> list:
    """Figure 4: Zoo test accuracy distribution histograms."""
    n_zoos = len(config.ZOO_NAMES)
    fig, axes = plt.subplots(1, n_zoos, figsize=(6 * n_zoos, 4))
    if n_zoos == 1:
        axes = [axes]

    for ax, zoo in zip(axes, config.ZOO_NAMES):
        accs = results.get(f"{zoo}_test_accuracies", [])
        if accs:
            accs = np.array(accs)
            ax.hist(accs, bins=40, edgecolor="black", alpha=0.7, color="#5B9BD5")
            mean_v = float(np.mean(accs))
            var_v = float(np.var(accs))
            ax.axvline(mean_v, color="red", linestyle="--", linewidth=2,
                       label=f"mean={mean_v:.3f}\nvar={var_v:.4f}")
            ax.set_xlabel("Test accuracy", fontsize=11)
            ax.set_ylabel("Count", fontsize=11)
            ax.set_title(f"{zoo.upper()} Zoo — Accuracy Distribution", fontsize=11)
            ax.legend(fontsize=9)
        else:
            ax.text(0.5, 0.5, "No data", ha="center", va="center",
                    transform=ax.transAxes, fontsize=14)
            ax.set_title(f"{zoo.upper()} Zoo", fontsize=11)

    plt.tight_layout()
    path = os.path.join(config.FIGURES_DIR, "fig4_diversity.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Figure 4 saved: {path}")
    return [path]
