"""Visualization for H-M1 analysis results."""
import logging
import os
import numpy as np

logger = logging.getLogger(__name__)


def _get_plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    return plt


def plot_preservation_rate(rates: dict, out_path: str) -> None:
    """Bar chart: preservation rate by benchmark vs 0.80 threshold."""
    plt = _get_plt()
    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
    splits = list(rates.keys())
    values = [rates[s] for s in splits]
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(splits, values, color="#4C72B0", alpha=0.85)
    ax.axhline(0.80, color="red", linestyle="--", linewidth=1.5, label="Gate threshold (0.80)")
    ax.set_ylim(0, 1.1)
    ax.set_ylabel("Preservation Rate")
    ax.set_title("H-M1: Label Preservation Rate by Benchmark")
    ax.legend()
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.01, f"{v:.3f}", ha="center", fontsize=9)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    logger.info("Saved preservation rate figure: %s", out_path)


def plot_stratum_ece(stratum_results: dict, out_path: str, clean_ece: float = 0.279) -> None:
    """Bar chart: ECE_clean vs ECE_adv per stratum."""
    plt = _get_plt()
    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
    splits = [s for s in stratum_results if s != "mnli"]
    eces = [stratum_results[s]["ece"] for s in splits]
    x = np.arange(len(splits))
    width = 0.35
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x - width / 2, [clean_ece] * len(splits), width, label=f"ECE_clean ({clean_ece:.3f})", color="#55A868", alpha=0.85)
    ax.bar(x + width / 2, eces, width, label="ECE_adv (stratum)", color="#C44E52", alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels(splits, rotation=30)
    ax.set_ylabel("ECE (15-bin)")
    ax.set_title("H-M1: ECE Clean vs Adversarial Strata")
    ax.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    logger.info("Saved stratum ECE figure: %s", out_path)


def plot_anli_gradient(stratum_results: dict, out_path: str) -> None:
    """Line chart: ΔECE vs ANLI round R1/R2/R3."""
    plt = _get_plt()
    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
    rounds = ["anli_r1", "anli_r2", "anli_r3"]
    deltas = [stratum_results.get(r, {}).get("delta_ece", None) for r in rounds]
    valid = [(i + 1, d) for i, d in enumerate(deltas) if d is not None]
    if not valid:
        logger.warning("No ANLI results for gradient plot")
        return
    xs, ys = zip(*valid)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(list(xs), list(ys), marker="o", linewidth=2, color="#4C72B0")
    ax.axhline(0, color="gray", linestyle="--", linewidth=1, label="ΔECE=0")
    ax.set_xticks(list(xs))
    ax.set_xticklabels([f"ANLI R{x}" for x in xs])
    ax.set_ylabel("ΔECE")
    ax.set_title("H-M1: ANLI Difficulty Gradient (ΔECE vs Round)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    logger.info("Saved ANLI gradient figure: %s", out_path)


def plot_reliability_diagrams(caches: dict, strata: dict, out_path: str, n_bins: int = 15) -> None:
    """Per-stratum reliability diagrams (confidence vs. accuracy per bin)."""
    plt = _get_plt()
    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
    splits = list(caches.keys())
    n_plots = len(splits)
    cols = min(3, n_plots)
    rows = (n_plots + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 4 * rows), squeeze=False)
    bin_edges = np.linspace(0, 1, n_bins + 1)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    for idx, split in enumerate(splits):
        ax = axes[idx // cols][idx % cols]
        cache = caches[split]
        split_strata = strata.get(split, {})
        # Use primary stratum (first key)
        if split_strata:
            mask = list(split_strata.values())[0]
        else:
            mask = np.ones(len(cache["conf"]), dtype=bool)

        conf = cache["conf"][mask]
        correct = cache["correct"][mask]

        accs, confs_mean, counts = [], [], []
        for lo, hi in zip(bin_edges[:-1], bin_edges[1:]):
            m = (conf > lo) & (conf <= hi)
            if m.sum() == 0:
                continue
            accs.append(correct[m].mean())
            confs_mean.append(conf[m].mean())
            counts.append(m.sum())

        ax.plot([0, 1], [0, 1], "k--", linewidth=1, alpha=0.5, label="Perfect calibration")
        ax.scatter(confs_mean, accs, s=np.array(counts) / max(counts) * 200 + 10, alpha=0.7)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xlabel("Mean Confidence")
        ax.set_ylabel("Accuracy")
        ax.set_title(f"{split} (n={mask.sum()})")
        ax.legend(fontsize=7)

    # Hide empty subplots
    for idx in range(n_plots, rows * cols):
        axes[idx // cols][idx % cols].set_visible(False)

    fig.suptitle("H-M1: Per-Stratum Reliability Diagrams", fontsize=12)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    logger.info("Saved reliability diagrams: %s", out_path)
