"""
visualization.py — H-M2 Pre-Softmax Logit Margin Inflation
Figure generation: 5 figures for gate chart, violin, scatter, heatmap, CDF.
"""
import logging
import os
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

logger = logging.getLogger(__name__)

# Color palette (consistent across all figures)
COLORS = {
    "ppo": "red",
    "dpo": "orange",
    "sft": "blue",
    "base": "gray",
}


def _get_margins_from_matrix(logprob_matrix: np.ndarray) -> np.ndarray:
    """Compute per-item margins from logprob matrix (N,4) -> margins (N,)."""
    sorted_lp = np.sort(logprob_matrix, axis=1)[:, ::-1]
    return sorted_lp[:, 0] - sorted_lp[:, 1]


def plot_delta_margin_bar(
    delta_results: dict,
    figures_dir: str,
    dpi: int = 150,
) -> str:
    """Grouped bar chart: PPO/DPO/SFT x 3 sizes with asymmetric 95% CI error bars.

    Colors: red=PPO, orange=DPO, blue=SFT. Dashed zero line.

    Returns:
        saved figure path (figure_01_delta_margin_gate.png)
    """
    sizes = ["1.4b", "2.8b", "6.9b"]
    alignments = ["ppo", "dpo", "sft"]

    fig, ax = plt.subplots(figsize=(12, 6))

    n_groups = len(sizes)
    n_bars = len(alignments)
    bar_width = 0.25
    x = np.arange(n_groups)

    for i, alignment in enumerate(alignments):
        means = []
        ci_lowers_err = []
        ci_uppers_err = []

        for size in sizes:
            key = f"{alignment}_{size}"
            if key in delta_results:
                dm, ci_lo, ci_hi = delta_results[key]
                means.append(dm)
                ci_lowers_err.append(dm - ci_lo)   # downward error
                ci_uppers_err.append(ci_hi - dm)   # upward error
            else:
                means.append(0.0)
                ci_lowers_err.append(0.0)
                ci_uppers_err.append(0.0)

        offset = (i - n_bars / 2 + 0.5) * bar_width
        bars = ax.bar(
            x + offset,
            means,
            width=bar_width,
            color=COLORS[alignment],
            alpha=0.8,
            label=alignment.upper(),
        )

        yerr = np.array([ci_lowers_err, ci_uppers_err])
        ax.errorbar(
            x + offset,
            means,
            yerr=yerr,
            fmt="none",
            color="black",
            capsize=4,
            linewidth=1.2,
        )

    # Zero reference line
    ax.axhline(y=0, color="black", linestyle="--", alpha=0.5, linewidth=1.2)

    ax.set_xlabel("Pythia Model Size", fontsize=12)
    ax.set_ylabel("Δ Logit Margin (nats)", fontsize=12)
    ax.set_title("H-M2: Alignment-Induced Logit Margin Inflation\n(SHOULD_WORK Gate)", fontsize=13)
    ax.set_xticks(x)
    ax.set_xticklabels([f"Pythia-{s}" for s in sizes])
    ax.legend(title="Alignment")
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    os.makedirs(figures_dir, exist_ok=True)
    out_path = os.path.join(figures_dir, "figure_01_delta_margin_gate.png")
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    logger.info("Figure 1 saved: %s", out_path)
    return out_path


def plot_margin_violin(
    logprob_matrices: dict,
    figures_dir: str,
    size: str = "1.4b",
    dpi: int = 150,
) -> str:
    """Violin plot: margin distributions for base vs PPO for given size.

    Returns:
        figure_02_margin_violin.png path
    """
    try:
        import seaborn as sns
    except ImportError:
        logger.warning("seaborn not available, using matplotlib violin")
        sns = None

    base_key = f"pythia-{size}-base"
    ppo_key = f"pythia-{size}-ppo"

    if base_key not in logprob_matrices or ppo_key not in logprob_matrices:
        logger.warning("Missing keys for violin: %s or %s", base_key, ppo_key)
        # Create placeholder figure
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, f"Missing data for {size}", ha="center", va="center")
        out_path = os.path.join(figures_dir, "figure_02_margin_violin.png")
        os.makedirs(figures_dir, exist_ok=True)
        fig.savefig(out_path, dpi=dpi)
        plt.close(fig)
        return out_path

    base_margins = _get_margins_from_matrix(logprob_matrices[base_key])
    ppo_margins = _get_margins_from_matrix(logprob_matrices[ppo_key])

    fig, ax = plt.subplots(figsize=(10, 6))

    if sns is not None:
        import pandas as pd
        df = pd.DataFrame({
            "Margin (nats)": np.concatenate([base_margins, ppo_margins]),
            "Model": (["Base"] * len(base_margins) + ["PPO"] * len(ppo_margins)),
        })
        sns.violinplot(
            data=df, x="Model", y="Margin (nats)",
            palette={"Base": COLORS["base"], "PPO": COLORS["ppo"]},
            ax=ax
        )
    else:
        ax.violinplot(
            [base_margins, ppo_margins],
            positions=[0, 1],
            showmeans=True,
        )
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["Base", "PPO"])

    ax.set_title(f"H-M2: Logit Margin Distribution — Pythia-{size}", fontsize=13)
    ax.set_xlabel("Model Type", fontsize=12)
    ax.set_ylabel("Logit Margin (nats)", fontsize=12)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    out_path = os.path.join(figures_dir, "figure_02_margin_violin.png")
    os.makedirs(figures_dir, exist_ok=True)
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    logger.info("Figure 2 saved: %s", out_path)
    return out_path


def load_delta_ece_from_validation(
    h_e1_validation_path: str,
) -> dict:
    """Parse h-e1/04_validation.md for ΔECE values for 9 model-size pairs.

    Returns:
        {"ppo_1.4b": float, "dpo_1.4b": float, "sft_1.4b": float, ...}
        Returns {} on FileNotFoundError or parse failure (non-fatal for figure 3).
    """
    if not os.path.exists(h_e1_validation_path):
        logger.warning("h-e1 validation report not found: %s", h_e1_validation_path)
        return {}

    try:
        with open(h_e1_validation_path, "r") as f:
            content = f.read()
    except Exception as e:
        logger.warning("Failed to read h-e1 validation report: %s", e)
        return {}

    delta_ece = {}
    sizes = ["1.4b", "2.8b", "6.9b"]
    alignments = ["sft", "dpo", "ppo"]

    # Try to parse ΔECE values from various table/metric formats
    # Pattern: look for key_metrics section or delta tables
    for alignment in alignments:
        for size in sizes:
            key = f"{alignment}_{size}"
            # Try various patterns: "dpo_1.4b_delta_rel", "Δ ECE dpo 1.4b", etc.
            patterns = [
                rf"{alignment}[_\s]*{re.escape(size)}[_\s]*delta[_\s]*(?:rel|ece)[:\s]+([-\d.]+)",
                rf"delta[_\s]*(?:rel|ece)[_\s]*{alignment}[_\s]*{re.escape(size)}[:\s]+([-\d.]+)",
                rf"\|\s*{alignment.upper()}\s+{re.escape(size)}\s*\|[^|]+\|\s*([-\d.]+)\s*\|",
            ]
            for pattern in patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    try:
                        delta_ece[key] = float(match.group(1))
                        break
                    except ValueError:
                        pass

    logger.info(
        "Parsed %d ΔECE values from %s", len(delta_ece), h_e1_validation_path
    )
    return delta_ece


def plot_delta_margin_vs_delta_ece(
    delta_results: dict,
    delta_ece: dict,
    figures_dir: str,
    dpi: int = 150,
) -> str:
    """Scatter: Δmargin vs ΔECE across 9 model-size pairs.

    Returns:
        figure_03_delta_margin_vs_delta_ece.png path
    """
    sizes = ["1.4b", "2.8b", "6.9b"]
    alignments = ["sft", "dpo", "ppo"]

    fig, ax = plt.subplots(figsize=(8, 6))

    if not delta_ece:
        ax.text(
            0.5, 0.5,
            "ΔECE data not available\n(h-e1/04_validation.md not parsed)",
            ha="center", va="center", fontsize=11
        )
        ax.set_title("H-M2: Δmargin vs ΔECE (data unavailable)", fontsize=13)
    else:
        x_vals, y_vals, colors, labels = [], [], [], []

        for alignment in alignments:
            for size in sizes:
                key = f"{alignment}_{size}"
                if key in delta_results and key in delta_ece:
                    x_vals.append(delta_ece[key])
                    y_vals.append(delta_results[key][0])
                    colors.append(COLORS[alignment])
                    labels.append(f"{alignment.upper()}-{size}")

        if x_vals:
            ax.scatter(x_vals, y_vals, c=colors, s=80, alpha=0.8, zorder=5)

            for xi, yi, label in zip(x_vals, y_vals, labels):
                ax.annotate(label, (xi, yi), textcoords="offset points",
                            xytext=(5, 5), fontsize=8, alpha=0.8)

            # Pearson r
            if len(x_vals) > 2:
                r = float(np.corrcoef(x_vals, y_vals)[0, 1])
                ax.text(
                    0.05, 0.95,
                    f"Pearson r = {r:.3f}",
                    transform=ax.transAxes,
                    va="top", ha="left", fontsize=10,
                    bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
                )

        ax.axhline(y=0, color="gray", linestyle="--", alpha=0.4)
        ax.axvline(x=0, color="gray", linestyle="--", alpha=0.4)
        ax.set_xlabel("ΔECE (alignment − base)", fontsize=12)
        ax.set_ylabel("Δ Logit Margin (nats)", fontsize=12)
        ax.set_title("H-M2: Δmargin vs ΔECE Across Model-Size Pairs", fontsize=13)
        ax.grid(alpha=0.3)

    plt.tight_layout()
    out_path = os.path.join(figures_dir, "figure_03_delta_margin_vs_delta_ece.png")
    os.makedirs(figures_dir, exist_ok=True)
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    logger.info("Figure 3 saved: %s", out_path)
    return out_path


def plot_gradient_ordering_heatmap(
    delta_results: dict,
    figures_dir: str,
    dpi: int = 150,
) -> str:
    """Heatmap: 3x3 (alignment x model_size) of Δmargin values.

    Rows: sft/dpo/ppo. Cols: 1.4b/2.8b/6.9b.

    Returns:
        figure_04_gradient_ordering_heatmap.png path
    """
    sizes = ["1.4b", "2.8b", "6.9b"]
    alignments = ["sft", "dpo", "ppo"]

    # Build 3x3 matrix
    data = np.zeros((3, 3))
    for i, alignment in enumerate(alignments):
        for j, size in enumerate(sizes):
            key = f"{alignment}_{size}"
            if key in delta_results:
                data[i, j] = delta_results[key][0]

    fig, ax = plt.subplots(figsize=(8, 6))

    try:
        import seaborn as sns
        sns.heatmap(
            data,
            xticklabels=[f"Pythia-{s}" for s in sizes],
            yticklabels=[a.upper() for a in alignments],
            annot=True,
            fmt=".4f",
            cmap="RdYlGn",
            center=0,
            ax=ax,
            cbar_kws={"label": "Δ Logit Margin (nats)"},
        )
    except ImportError:
        im = ax.imshow(data, cmap="RdYlGn", aspect="auto")
        plt.colorbar(im, ax=ax, label="Δ Logit Margin (nats)")
        ax.set_xticks(range(3))
        ax.set_xticklabels([f"Pythia-{s}" for s in sizes])
        ax.set_yticks(range(3))
        ax.set_yticklabels([a.upper() for a in alignments])
        for i in range(3):
            for j in range(3):
                ax.text(j, i, f"{data[i,j]:.4f}", ha="center", va="center", fontsize=9)

    ax.set_title("H-M2: Gradient Ordering Heatmap (Δmargin)", fontsize=13)
    ax.set_xlabel("Model Size", fontsize=12)
    ax.set_ylabel("Alignment Method", fontsize=12)

    plt.tight_layout()
    out_path = os.path.join(figures_dir, "figure_04_gradient_ordering_heatmap.png")
    os.makedirs(figures_dir, exist_ok=True)
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    logger.info("Figure 4 saved: %s", out_path)
    return out_path


def plot_margin_cdf(
    logprob_matrices: dict,
    figures_dir: str,
    size: str = "1.4b",
    dpi: int = 150,
) -> str:
    """CDF of margins: base vs PPO for given size.

    Returns:
        figure_05_margin_cdf.png path
    """
    base_key = f"pythia-{size}-base"
    ppo_key = f"pythia-{size}-ppo"

    fig, ax = plt.subplots(figsize=(8, 6))

    for key, label, color in [
        (base_key, "Base", COLORS["base"]),
        (ppo_key, "PPO", COLORS["ppo"]),
    ]:
        if key in logprob_matrices:
            margins = _get_margins_from_matrix(logprob_matrices[key])
            sorted_margins = np.sort(margins)
            N = len(sorted_margins)
            cdf = np.arange(1, N + 1) / N
            ax.plot(sorted_margins, cdf, color=color, label=label, linewidth=1.5)
        else:
            logger.warning("Missing key for CDF: %s", key)

    ax.set_xlabel("Logit Margin (nats)", fontsize=12)
    ax.set_ylabel("CDF", fontsize=12)
    ax.set_title(f"H-M2: Empirical CDF of Logit Margins — Pythia-{size}", fontsize=13)
    ax.legend()
    ax.grid(alpha=0.3)

    plt.tight_layout()
    out_path = os.path.join(figures_dir, "figure_05_margin_cdf.png")
    os.makedirs(figures_dir, exist_ok=True)
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    logger.info("Figure 5 saved: %s", out_path)
    return out_path


def generate_all_figures(
    delta_results: dict,
    logprob_matrices: dict,
    h_e1_validation_path: str,
    figures_dir: str,
    dpi: int = 150,
) -> list:
    """Generate all 5 figures.

    Returns:
        list of saved paths (len 5)
    """
    logger.info("Generating all 5 figures...")

    figure_paths = []

    # Figure 1: Delta margin gate bar chart
    try:
        p = plot_delta_margin_bar(delta_results, figures_dir, dpi=dpi)
        figure_paths.append(p)
    except Exception as e:
        logger.error("Figure 1 failed: %s", e)
        figure_paths.append("FAILED: figure_01")

    # Figure 2: Violin plot (base vs PPO, 1.4b)
    try:
        p = plot_margin_violin(logprob_matrices, figures_dir, size="1.4b", dpi=dpi)
        figure_paths.append(p)
    except Exception as e:
        logger.error("Figure 2 failed: %s", e)
        figure_paths.append("FAILED: figure_02")

    # Figure 3: Scatter Δmargin vs ΔECE
    try:
        delta_ece = load_delta_ece_from_validation(h_e1_validation_path)
        p = plot_delta_margin_vs_delta_ece(delta_results, delta_ece, figures_dir, dpi=dpi)
        figure_paths.append(p)
    except Exception as e:
        logger.error("Figure 3 failed: %s", e)
        figure_paths.append("FAILED: figure_03")

    # Figure 4: Gradient ordering heatmap
    try:
        p = plot_gradient_ordering_heatmap(delta_results, figures_dir, dpi=dpi)
        figure_paths.append(p)
    except Exception as e:
        logger.error("Figure 4 failed: %s", e)
        figure_paths.append("FAILED: figure_04")

    # Figure 5: CDF (base vs PPO, 1.4b)
    try:
        p = plot_margin_cdf(logprob_matrices, figures_dir, size="1.4b", dpi=dpi)
        figure_paths.append(p)
    except Exception as e:
        logger.error("Figure 5 failed: %s", e)
        figure_paths.append("FAILED: figure_05")

    logger.info("Figures generated: %d/5", len([p for p in figure_paths if not p.startswith("FAILED")]))
    return figure_paths
