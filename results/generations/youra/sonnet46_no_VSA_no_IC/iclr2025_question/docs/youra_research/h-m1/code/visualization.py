import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List

VIZ_CONFIG = {
    "color_hallucinated": "#E74C3C",
    "color_correct":      "#2ECC71",
    "palette": {"hallucinated": "#E74C3C", "correct": "#2ECC71"},
    "figsize_bar":     (8, 5),
    "figsize_kde":     (7, 5),
    "figsize_scatter": (7, 6),
    "figsize_boxplot": (8, 5),
    "dpi": 150,
    "fname_bar":     "peakedness_bar_comparison.png",
    "fname_kde":     "peakedness_kde_{dataset}.png",
    "fname_scatter": "peakedness_scatter_auroc.png",
    "fname_boxplot": "peakedness_boxplot.png",
}


def _ci95(data: List[float]) -> float:
    """95% CI half-width via normal approximation."""
    if len(data) < 2:
        return 0.0
    return 1.96 * np.std(data, ddof=1) / np.sqrt(len(data))


def plot_bar_comparison(
    group_data: Dict[str, Dict[str, List[float]]],
    save_path: str,
) -> None:
    """Bar chart: mean peakedness ± 95% CI, hallucinated vs correct, by dataset. MANDATORY gate figure."""
    datasets = sorted(group_data.keys())
    groups = ["hallucinated", "correct"]
    x = np.arange(len(datasets))
    width = 0.35

    fig, ax = plt.subplots(figsize=VIZ_CONFIG["figsize_bar"])
    for i, grp in enumerate(groups):
        means = [np.mean(group_data[ds][grp]) for ds in datasets]
        cis = [_ci95(group_data[ds][grp]) for ds in datasets]
        ax.bar(x + i * width, means, width, yerr=cis, capsize=4,
               label=grp.capitalize(), color=VIZ_CONFIG["palette"][grp], alpha=0.85)

    ax.set_xlabel("Dataset")
    ax.set_ylabel("Mean Peakedness (max|lp|/mean|lp|)")
    ax.set_title("Token Log-Prob Peakedness: Hallucinated vs Correct")
    ax.set_xticks(x + width / 2)
    ax.set_xticklabels(datasets)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(save_path, dpi=VIZ_CONFIG["dpi"])
    plt.close(fig)


def plot_kde_distributions(
    group_data: Dict[str, List[float]],
    dataset_name: str,
    save_path: str,
) -> None:
    """Overlapping KDE plots per dataset."""
    fig, ax = plt.subplots(figsize=VIZ_CONFIG["figsize_kde"])
    for grp in ["hallucinated", "correct"]:
        data = group_data[grp]
        if not data:
            continue
        arr = np.array(data)
        # clip for display
        arr = arr[arr < np.percentile(arr, 99)]
        ax.hist(arr, bins=50, density=True, alpha=0.5,
                label=grp.capitalize(), color=VIZ_CONFIG["palette"][grp])
    ax.set_xlabel("Peakedness Ratio")
    ax.set_ylabel("Density")
    ax.set_title(f"Peakedness Distribution — {dataset_name}")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(save_path, dpi=VIZ_CONFIG["dpi"])
    plt.close(fig)


def plot_scatter_auroc(
    peakedness: List[float],
    auroc_scores: List[float],
    labels: List[int],
    save_path: str,
) -> None:
    """Peakedness ratio vs H-E1 AUROC score per sample."""
    fig, ax = plt.subplots(figsize=VIZ_CONFIG["figsize_scatter"])
    p_arr = np.array(peakedness)
    a_arr = np.array(auroc_scores)
    l_arr = np.array(labels)
    for lv, grp in [(0, "hallucinated"), (1, "correct")]:
        mask = l_arr == lv
        ax.scatter(p_arr[mask], a_arr[mask], alpha=0.3, s=8,
                   label=grp.capitalize(), color=VIZ_CONFIG["palette"][grp])
    ax.set_xlabel("Peakedness Ratio")
    ax.set_ylabel("Per-sample Score")
    ax.set_title("Peakedness vs Sample Score")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(save_path, dpi=VIZ_CONFIG["dpi"])
    plt.close(fig)


def plot_boxplot(
    group_data: Dict[str, Dict[str, List[float]]],
    save_path: str,
) -> None:
    """Boxplot: peakedness by (dataset, label) — 4 boxes."""
    datasets = sorted(group_data.keys())
    fig, ax = plt.subplots(figsize=VIZ_CONFIG["figsize_boxplot"])
    positions = []
    all_data = []
    tick_labels = []
    pos = 1
    for ds in datasets:
        for grp in ["hallucinated", "correct"]:
            all_data.append(group_data[ds][grp])
            positions.append(pos)
            tick_labels.append(f"{ds}\n{grp[:4]}")
            pos += 1
        pos += 0.5  # gap between datasets

    bp = ax.boxplot(all_data, positions=positions, patch_artist=True, showfliers=False)
    colors = []
    for ds in datasets:
        colors.extend([VIZ_CONFIG["color_hallucinated"], VIZ_CONFIG["color_correct"]])
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax.set_xticks(positions)
    ax.set_xticklabels(tick_labels, fontsize=8)
    ax.set_ylabel("Peakedness Ratio")
    ax.set_title("Peakedness Distribution by Dataset and Label")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(save_path, dpi=VIZ_CONFIG["dpi"])
    plt.close(fig)


def save_all_figures(all_results: Dict, figures_dir: str) -> None:
    """Generate and save all 4 required figures."""
    import os
    os.makedirs(figures_dir, exist_ok=True)

    # Build group_data: {dataset_key: {"hallucinated": [...], "correct": [...]}}
    group_data = {}
    for key, res in all_results.items():
        group_data[key] = {
            "hallucinated": res["hallucinated"],
            "correct": res["correct"],
        }

    # 1. Bar comparison (mandatory gate figure)
    plot_bar_comparison(
        group_data,
        os.path.join(figures_dir, VIZ_CONFIG["fname_bar"]),
    )

    # 2. KDE per dataset
    for key, gd in group_data.items():
        plot_kde_distributions(
            gd,
            key,
            os.path.join(figures_dir, VIZ_CONFIG["fname_kde"].format(dataset=key)),
        )

    # 3. Boxplot
    plot_boxplot(
        group_data,
        os.path.join(figures_dir, VIZ_CONFIG["fname_boxplot"]),
    )

    # 4. Scatter (peakedness vs mean_score proxy — use label as proxy if no auroc)
    # Aggregate all samples across datasets for scatter
    all_peak = []
    all_labels = []
    for res in all_results.values():
        n_h = len(res["hallucinated"])
        n_c = len(res["correct"])
        all_peak.extend(res["hallucinated"])
        all_peak.extend(res["correct"])
        all_labels.extend([0] * n_h)
        all_labels.extend([1] * n_c)
    # Use peakedness itself as y-axis proxy (no H-E1 per-sample AUROC available)
    # scatter: x=peakedness, y=label (0/1) with jitter
    rng = np.random.default_rng(42)
    jitter = rng.uniform(-0.1, 0.1, len(all_labels))
    plot_scatter_auroc(
        all_peak,
        (np.array(all_labels) + jitter).tolist(),
        all_labels,
        os.path.join(figures_dir, VIZ_CONFIG["fname_scatter"]),
    )
