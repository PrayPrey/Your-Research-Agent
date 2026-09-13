import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from scipy import stats as _stats


def plot_gap_curve(kl, gap, high_kl_mask, max_gap, figs_dir, dpi=150):
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(kl, gap, marker="o", color="royalblue", linewidth=2,
            label="Divergence Gap (RM_norm − gold)")
    ax.axhline(y=0, color="black", linestyle="--", alpha=0.6, label="Zero line")
    ax.fill_between(kl, gap, 0, where=(gap > 0),
                    alpha=0.15, color="royalblue", label="Positive gap region")
    max_idx = int(gap.argmax())
    ax.annotate(
        f"max_gap={max_gap:.3f}",
        xy=(kl[max_idx], gap[max_idx]),
        xytext=(10, -15), textcoords="offset points",
        fontsize=9, arrowprops=dict(arrowstyle="->", color="gray")
    )
    if high_kl_mask.any():
        boundary_kl = kl[high_kl_mask].min()
        ax.axvline(x=boundary_kl, color="orange", linestyle=":",
                   alpha=0.7, label=f"High-KL boundary (KL>{boundary_kl:.2f})")
    ax.set_xlabel("KL Budget (nats)")
    ax.set_ylabel("gap = RM_norm − gold_preference")
    ax.set_title("H-M2: Calibration-Alignment Divergence Gap vs KL Budget")
    ax.legend(fontsize=9)
    fig.tight_layout()
    Path(figs_dir).mkdir(parents=True, exist_ok=True)
    out_path = str(Path(figs_dir) / "gap_curve.png")
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)
    return out_path


def plot_dual_line(kl, rm_norm, gold, figs_dir, dpi=150):
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(kl, rm_norm, marker="o", color="steelblue", linewidth=2,
            label="RM Score (normalized)")
    ax.plot(kl, gold, marker="s", linestyle="--", color="crimson", linewidth=2,
            label="Gold Preference Rate")
    crossover = (rm_norm > gold)
    if crossover.any():
        cx_idx = int(crossover.argmax())
        ax.annotate(
            f"Crossover\nKL≈{kl[cx_idx]:.1f}",
            xy=(kl[cx_idx], rm_norm[cx_idx]),
            xytext=(10, 15), textcoords="offset points",
            fontsize=8, arrowprops=dict(arrowstyle="->", color="gray")
        )
    ax.set_xlabel("KL Budget (nats)")
    ax.set_ylabel("Value [0, 1]")
    ax.set_ylim(-0.05, 1.05)
    ax.set_title("H-M2: RM_norm vs Gold Preference — Same [0,1] Scale")
    ax.legend(fontsize=9)
    fig.tight_layout()
    Path(figs_dir).mkdir(parents=True, exist_ok=True)
    out_path = str(Path(figs_dir) / "dual_line.png")
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)
    return out_path


def plot_gap_scatter(kl, gap, rho, high_kl_mask, figs_dir, dpi=150):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(kl[~high_kl_mask], gap[~high_kl_mask],
               color="steelblue", s=70, zorder=5, label="Low-KL levels")
    ax.scatter(kl[high_kl_mask], gap[high_kl_mask],
               color="darkorange", s=90, marker="D", zorder=6, label="High-KL levels")
    slope, intercept, *_ = _stats.linregress(kl, gap)
    kl_line = np.linspace(kl.min(), kl.max(), 100)
    ax.plot(kl_line, slope * kl_line + intercept,
            color="navy", linestyle="--", alpha=0.5, label="OLS trend")
    ax.axhline(y=0, color="black", linestyle=":", alpha=0.4)
    ax.set_xlabel("KL Budget (nats)")
    ax.set_ylabel("gap = RM_norm − gold_preference")
    ax.set_title(f"H-M2: Gap Growth vs KL Budget  |  Spearman ρ = {rho:.3f}")
    ax.legend(fontsize=9)
    fig.tight_layout()
    Path(figs_dir).mkdir(parents=True, exist_ok=True)
    out_path = str(Path(figs_dir) / "gap_scatter.png")
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)
    return out_path


def plot_gate_metrics(results, figs_dir, dpi=150):
    metrics = {
        "n_positive\nhigh_kl": (results["n_positive_high_kl"], 3,
                                 results["n_positive_high_kl"] >= 3),
        "ρ(KL,gap)":           (results["rho_gap_kl"], 0.0,
                                 results["rho_gap_kl"] > 0),
        "prop_positive":        (results["prop_positive"], 0.5,
                                 results["prop_positive"] > 0.5),
    }
    fig, ax = plt.subplots(figsize=(8, 5))
    x = list(range(len(metrics)))
    colors = ["forestgreen" if v[2] else "tomato" for v in metrics.values()]
    ax.bar(x, [v[0] for v in metrics.values()], color=colors, alpha=0.75, width=0.5)
    for i, (label, (val, threshold, passed)) in enumerate(metrics.items()):
        ax.hlines(y=threshold, xmin=i - 0.3, xmax=i + 0.3,
                  colors="black", linestyles="--", linewidth=1.5)
        ax.text(i, threshold + 0.03, f"threshold={threshold}",
                ha="center", fontsize=8)
        ax.text(i, val + 0.05, f"{val:.3f}" if isinstance(val, float) else str(val),
                ha="center", fontsize=9, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(list(metrics.keys()))
    ax.set_ylabel("Metric Value")
    gate = "PASS" if results["gate_pass"] else "FAIL"
    ax.set_title(f"H-M2 Gate Metrics — {gate}")
    fig.tight_layout()
    Path(figs_dir).mkdir(parents=True, exist_ok=True)
    out_path = str(Path(figs_dir) / "gate_metrics.png")
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)
    return out_path
