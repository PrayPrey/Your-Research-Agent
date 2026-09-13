"""
plot_results.py — H-E1: Visualization
Implements 5 figures: delta_reliability_bar, calibration_curves, ece_heatmap,
                       brier_decomposition, bootstrap_ci_distributions
"""

import argparse
import json
import os

import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

FIGURES_DIR: str = "./figures"
SIZES = ["1.4b", "2.8b", "6.9b"]
ALIGNMENTS = ["sft", "dpo", "ppo"]
COLORS = {"sft": "#2196F3", "dpo": "#FF9800", "ppo": "#F44336"}


def _load_results(results_dir: str) -> dict:
    json_path = os.path.join(results_dir, "calibration_results.json")
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"calibration_results.json not found at {json_path}")
    with open(json_path) as f:
        return json.load(f)


def plot_delta_reliability_bar(results: dict, out_dir: str = FIGURES_DIR) -> None:
    """Grouped bar chart: ΔBrier reliability with 95% CI error bars per size × alignment.
    MANDATORY figure."""
    os.makedirs(out_dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(SIZES))
    n_align = len(ALIGNMENTS)
    width = 0.25

    for i, alignment in enumerate(ALIGNMENTS):
        deltas = []
        errs_lo = []
        errs_hi = []
        for size in SIZES:
            key = f"pythia-{size}-{alignment}"
            m = results.get(key, {})
            delta = m.get("delta_rel")
            ci_lo = m.get("ci_lower")
            ci_hi = m.get("ci_upper")
            if delta is None:
                delta, ci_lo, ci_hi = 0.0, 0.0, 0.0
            deltas.append(delta)
            errs_lo.append(abs(delta - (ci_lo or delta)))
            errs_hi.append(abs((ci_hi or delta) - delta))

        offset = (i - n_align / 2 + 0.5) * width
        bars = ax.bar(x + offset, deltas, width, label=alignment.upper(),
                      color=COLORS[alignment], alpha=0.85)
        ax.errorbar(
            x + offset, deltas,
            yerr=[errs_lo, errs_hi],
            fmt="none", color="black", capsize=4, linewidth=1.5,
        )

    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_xlabel("Pythia Model Size", fontsize=13)
    ax.set_ylabel("ΔBrier Reliability (aligned − base)", fontsize=13)
    ax.set_title("Alignment-Induced Brier Reliability Increase (H-E1 Gate: MUST_WORK)", fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels([f"Pythia-{s}" for s in SIZES])
    ax.legend(title="Alignment")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()

    out_path = os.path.join(out_dir, "delta_reliability_bar.png")
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"✅ Saved: {out_path}")


def plot_calibration_curves(results: dict, out_dir: str = FIGURES_DIR) -> None:
    """3×3 reliability diagram grid: base vs SFT/DPO/PPO per size.
    NOTE: Requires raw logprobs; uses ECE as proxy if curves not available."""
    os.makedirs(out_dir, exist_ok=True)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("Calibration Curves by Model Size (ECE proxy)", fontsize=14)

    for col, size in enumerate(SIZES):
        ax = axes[col]
        ax.plot([0, 1], [0, 1], "k--", linewidth=1, label="Perfect")

        for cond in ["base"] + ALIGNMENTS:
            key = f"pythia-{size}-{cond}"
            m = results.get(key, {})
            ece = m.get("ece")
            if ece is None:
                continue
            color = "black" if cond == "base" else COLORS.get(cond, "gray")
            # Represent calibration quality as diagonal offset placeholder
            ax.annotate(
                f"{cond.upper()}\nECE={ece:.3f}",
                xy=(0.05, 0.85 - 0.15 * ["base", "sft", "dpo", "ppo"].index(cond)),
                xycoords="axes fraction",
                fontsize=8,
                color=color,
            )

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xlabel("Mean Predicted Prob")
        ax.set_ylabel("Fraction Correct")
        ax.set_title(f"Pythia-{size}")
        ax.grid(alpha=0.3)

    fig.tight_layout()
    out_path = os.path.join(out_dir, "calibration_curves.png")
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"✅ Saved: {out_path}")


def plot_ece_heatmap(results: dict, out_dir: str = FIGURES_DIR) -> None:
    """3 sizes × 4 conditions ECE heatmap."""
    os.makedirs(out_dir, exist_ok=True)

    conditions = ["base"] + ALIGNMENTS
    data = np.zeros((len(SIZES), len(conditions)))
    mask = np.ones_like(data, dtype=bool)

    for r, size in enumerate(SIZES):
        for c, cond in enumerate(conditions):
            key = f"pythia-{size}-{cond}"
            ece = results.get(key, {}).get("ece")
            if ece is not None:
                data[r, c] = ece
                mask[r, c] = False

    fig, ax = plt.subplots(figsize=(8, 5))
    im = ax.imshow(data, aspect="auto", cmap="RdYlGn_r", vmin=0, vmax=0.3)
    plt.colorbar(im, ax=ax, label="ECE")

    ax.set_xticks(range(len(conditions)))
    ax.set_xticklabels([c.upper() for c in conditions])
    ax.set_yticks(range(len(SIZES)))
    ax.set_yticklabels([f"Pythia-{s}" for s in SIZES])
    ax.set_title("ECE Heatmap: 3 Sizes × 4 Alignment Conditions")

    for r in range(len(SIZES)):
        for c in range(len(conditions)):
            if not mask[r, c]:
                ax.text(c, r, f"{data[r, c]:.3f}", ha="center", va="center", fontsize=9)

    fig.tight_layout()
    out_path = os.path.join(out_dir, "ece_heatmap.png")
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"✅ Saved: {out_path}")


def plot_brier_decomposition(results: dict, out_dir: str = FIGURES_DIR) -> None:
    """Stacked bar: reliability / resolution / uncertainty per model."""
    os.makedirs(out_dir, exist_ok=True)

    model_keys = [f"pythia-{s}-{c}" for s in SIZES for c in ["base"] + ALIGNMENTS]
    model_labels = [f"{s}\n{c.upper()}" for s in SIZES for c in ["base"] + ALIGNMENTS]

    rels, ress, uncs = [], [], []
    valid_keys, valid_labels = [], []

    for key, label in zip(model_keys, model_labels):
        m = results.get(key, {})
        if m.get("brier_rel") is not None:
            rels.append(m["brier_rel"])
            ress.append(m.get("brier_res", 0) or 0)
            uncs.append(m.get("brier_unc", 0) or 0)
            valid_keys.append(key)
            valid_labels.append(label)

    if not valid_keys:
        print("⚠️ No data for brier_decomposition plot")
        return

    x = np.arange(len(valid_keys))
    fig, ax = plt.subplots(figsize=(max(10, len(valid_keys) * 0.9), 6))

    ax.bar(x, rels, label="Reliability (REL)", color="#F44336", alpha=0.85)
    ax.bar(x, ress, bottom=rels, label="Resolution (RES)", color="#2196F3", alpha=0.85)
    ax.bar(x, uncs, bottom=np.array(rels) + np.array(ress),
           label="Uncertainty (UNC)", color="#4CAF50", alpha=0.85)

    ax.set_xlabel("Model")
    ax.set_ylabel("Brier Component")
    ax.set_title("Brier Score Decomposition: REL / RES / UNC per Model")
    ax.set_xticks(x)
    ax.set_xticklabels(valid_labels, fontsize=7, rotation=45, ha="right")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()

    out_path = os.path.join(out_dir, "brier_decomposition.png")
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"✅ Saved: {out_path}")


def plot_bootstrap_ci_distributions(results: dict, out_dir: str = FIGURES_DIR) -> None:
    """Delta distributions with 95% CI bands (point estimates + CI ranges)."""
    os.makedirs(out_dir, exist_ok=True)

    fig, axes = plt.subplots(1, len(SIZES), figsize=(14, 5), sharey=False)
    fig.suptitle("Bootstrap 95% CI for ΔBrier Reliability (aligned − base)", fontsize=13)

    for col, size in enumerate(SIZES):
        ax = axes[col]
        ax.axhline(0, color="black", linewidth=0.8, linestyle="--")

        for i, alignment in enumerate(ALIGNMENTS):
            key = f"pythia-{size}-{alignment}"
            m = results.get(key, {})
            delta = m.get("delta_rel")
            ci_lo = m.get("ci_lower")
            ci_hi = m.get("ci_upper")
            if delta is None:
                continue
            color = COLORS[alignment]
            ax.errorbar(
                i, delta,
                yerr=[[abs(delta - ci_lo)], [abs(ci_hi - delta)]],
                fmt="o", color=color, capsize=6, linewidth=2,
                markersize=8, label=alignment.upper(),
            )

        ax.set_xticks(range(len(ALIGNMENTS)))
        ax.set_xticklabels([a.upper() for a in ALIGNMENTS])
        ax.set_xlabel("Alignment")
        ax.set_ylabel("Δ Brier Reliability")
        ax.set_title(f"Pythia-{size}")
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)

    fig.tight_layout()
    out_path = os.path.join(out_dir, "bootstrap_ci_distributions.png")
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"✅ Saved: {out_path}")


def generate_all_figures(results_dir: str = "./results", figures_dir: str = FIGURES_DIR) -> None:
    """Generate all 5 figures from calibration_results.json."""
    results = _load_results(results_dir)
    os.makedirs(figures_dir, exist_ok=True)
    plot_delta_reliability_bar(results, figures_dir)
    plot_calibration_curves(results, figures_dir)
    plot_ece_heatmap(results, figures_dir)
    plot_brier_decomposition(results, figures_dir)
    plot_bootstrap_ci_distributions(results, figures_dir)
    print(f"\n✅ All 5 figures saved to: {figures_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="H-E1 Result Visualization")
    parser.add_argument("--results-dir", default="./results")
    parser.add_argument("--figures-dir", default=FIGURES_DIR)
    args = parser.parse_args()
    generate_all_figures(args.results_dir, args.figures_dir)
