from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from config import ExperimentConfig


def plot_gate_metrics_bar(cv: float, tau: float, cfg: ExperimentConfig, save_path: Path) -> None:
    """Bar chart: CV vs 0.3 threshold, tau vs 0.6 threshold."""
    fig, ax = plt.subplots(figsize=(6, 5))

    metrics    = [cv, tau]
    thresholds = [cfg.cv_threshold, cfg.tau_threshold]
    labels     = ["CV (epsilon=0.01)", "Kendall tau\n(Alpaca vs WikiText)"]
    colors     = ["steelblue" if v > t else "tomato" for v, t in zip(metrics, thresholds)]

    bars = ax.bar(labels, metrics, color=colors, edgecolor="black", width=0.4)

    ax.axhline(cfg.cv_threshold,  color="steelblue",  linestyle="--", alpha=0.7,
               label=f"CV threshold={cfg.cv_threshold}")
    ax.axhline(cfg.tau_threshold, color="darkorange", linestyle="--", alpha=0.7,
               label=f"tau threshold={cfg.tau_threshold}")

    for bar, val in zip(bars, metrics):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                f"{val:.3f}", ha="center", va="bottom", fontsize=11)

    ax.set_ylabel("Metric Value")
    ax.set_title("Gate Condition Metrics (H-E1)")
    ax.set_ylim(0, max(max(metrics), 1.0) * 1.15)
    ax.legend(fontsize=9)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_sparsity_profile(
    alpaca_sparsity: np.ndarray,
    wikitext_sparsity: np.ndarray,
    epsilon: float,
    cfg: ExperimentConfig,
    save_path: Path,
) -> None:
    """Per-layer sparsity line plot, Alpaca vs WikiText overlaid."""
    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(cfg.n_layers)

    ax.plot(x, alpaca_sparsity,   label="Alpaca (512-tok)",       marker="o", linewidth=1.5)
    ax.plot(x, wikitext_sparsity, label="WikiText-103 (512-tok)", marker="s", linewidth=1.5)

    ax.set_xlabel("Layer Index")
    ax.set_ylabel(f"Mean Sparsity Fraction (|a| < {epsilon})")
    ax.set_title(f"Per-Layer Activation Sparsity (epsilon={epsilon})")
    ax.set_xticks(x[::4])
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_epsilon_sensitivity(metrics: dict, cfg: ExperimentConfig, save_path: Path) -> None:
    """Heatmap showing CV and tau for each epsilon value."""
    epsilons = cfg.epsilons
    cv_vals  = [metrics.get(f"cv_alpaca_long_eps{e}", 0.0) for e in epsilons]
    tau_vals = [metrics.get(f"tau_calibration_eps{e}", 0.0) for e in epsilons]

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    axes[0].bar([str(e) for e in epsilons], cv_vals, color="steelblue", edgecolor="black")
    axes[0].axhline(cfg.cv_threshold, color="red", linestyle="--", label=f"threshold={cfg.cv_threshold}")
    axes[0].set_title("CV vs Epsilon")
    axes[0].set_xlabel("Epsilon")
    axes[0].set_ylabel("CV")
    axes[0].legend()

    axes[1].bar([str(e) for e in epsilons], tau_vals, color="darkorange", edgecolor="black")
    axes[1].axhline(cfg.tau_threshold, color="red", linestyle="--", label=f"threshold={cfg.tau_threshold}")
    axes[1].set_title("Kendall tau (Calibration) vs Epsilon")
    axes[1].set_xlabel("Epsilon")
    axes[1].set_ylabel("Kendall tau")
    axes[1].legend()

    plt.suptitle("Epsilon Sensitivity Analysis (H-E1)")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_length_sensitivity(
    alpaca_short_sparsity: np.ndarray,
    alpaca_long_sparsity: np.ndarray,
    tau_length: float,
    cfg: ExperimentConfig,
    save_path: Path,
) -> None:
    """Two overlaid lines: 128-token vs 512-token Alpaca; annotate tau_length."""
    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(cfg.n_layers)

    ax.plot(x, alpaca_short_sparsity, label=f"Alpaca {cfg.short_length}-tok", marker="o", linewidth=1.5)
    ax.plot(x, alpaca_long_sparsity,  label=f"Alpaca {cfg.long_length}-tok",  marker="s", linewidth=1.5)

    ax.text(0.98, 0.95, f"tau_length = {tau_length:.3f}",
            transform=ax.transAxes, ha="right", va="top", fontsize=11,
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))

    ax.set_xlabel("Layer Index")
    ax.set_ylabel("Mean Sparsity Fraction")
    ax.set_title("Length Sensitivity: Short vs Long Context")
    ax.set_xticks(x[::4])
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_rank_correlation_scatter(
    alpaca_sparsity: np.ndarray,
    wikitext_sparsity: np.ndarray,
    tau: float,
    p_value: float,
    cfg: ExperimentConfig,
    save_path: Path,
) -> None:
    """Scatter of rank arrays (Alpaca vs WikiText) with Kendall tau annotation."""
    alpaca_ranks   = np.argsort(np.argsort(alpaca_sparsity))
    wikitext_ranks = np.argsort(np.argsort(wikitext_sparsity))

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(alpaca_ranks, wikitext_ranks, s=60, edgecolors="black", alpha=0.8)

    ax.plot([0, cfg.n_layers - 1], [0, cfg.n_layers - 1], "k--", alpha=0.4,
            label="Perfect rank agreement")

    ax.text(0.05, 0.92, f"Kendall tau = {tau:.3f}\np = {p_value:.3e}",
            transform=ax.transAxes, fontsize=11, verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))

    ax.set_xlabel("Alpaca Layer Rank (by sparsity)")
    ax.set_ylabel("WikiText-103 Layer Rank (by sparsity)")
    ax.set_title("Rank Correlation: Alpaca vs WikiText-103")
    ax.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def generate_all_figures(condition_results: dict, metrics: dict, cfg: ExperimentConfig) -> None:
    """Orchestrate all 5 figures."""
    figures_dir = Path(cfg.figures_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)

    eps = cfg.primary_epsilon

    alpaca_long   = condition_results[("alpaca",   eps, cfg.long_length)]
    alpaca_short  = condition_results[("alpaca",   eps, cfg.short_length)]
    wikitext_long = condition_results[("wikitext", eps, cfg.long_length)]

    cv  = metrics["cv_primary"]
    tau = metrics["tau_calibration"]
    tau_len   = metrics["tau_length"]
    p_val     = metrics["tau_calibration_pval"]

    plot_gate_metrics_bar(cv, tau, cfg, figures_dir / "gate_metrics.png")
    print("  Saved gate_metrics.png")

    plot_sparsity_profile(alpaca_long, wikitext_long, eps, cfg, figures_dir / "sparsity_profile.png")
    print("  Saved sparsity_profile.png")

    plot_epsilon_sensitivity(metrics, cfg, figures_dir / "epsilon_sensitivity.png")
    print("  Saved epsilon_sensitivity.png")

    plot_length_sensitivity(alpaca_short, alpaca_long, tau_len, cfg, figures_dir / "length_sensitivity.png")
    print("  Saved length_sensitivity.png")

    plot_rank_correlation_scatter(alpaca_long, wikitext_long, tau, p_val, cfg,
                                  figures_dir / "rank_correlation.png")
    print("  Saved rank_correlation.png")

    print(f"All 5 figures saved to {figures_dir}/")
