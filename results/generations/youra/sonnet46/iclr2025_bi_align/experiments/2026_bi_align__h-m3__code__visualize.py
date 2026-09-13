"""
visualize.py - Visualization functions for h-e1/h-m1 experiment.

h-m1 extension: 7 tier-comparison plot functions for multi-model tier analysis.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# ============================================================================
# H-M1 Configuration Constants (Tasks C-6-1, C-6-2, C-6-3)
# ============================================================================

TIER_ORDER = ["helpful-base", "helpful-rejection-sampled", "helpful-online"]

TIER_COLORS = {
    "helpful-base": "#4878CF",          # blue (T1 lowest)
    "helpful-rejection-sampled": "#6ACC65",  # green (T2 middle)
    "helpful-online": "#D65F5F",        # red (T3 highest)
}

TIER_LABELS = {
    "helpful-base": "T1: Base",
    "helpful-rejection-sampled": "T2: Rejection-Sampled",
    "helpful-online": "T3: Online",
}

MODEL_DISPLAY_NAMES = {
    "minilm": "MiniLM-L6-v2",
    "paraphrase": "Paraphrase-MiniLM",
    "mpnet": "MPNet-base-v2",
}

DIRECTION_COLORS = {'H_given_A': '#4878CF', 'A_given_H': '#D65F5F'}
DIRECTION_LABELS = {
    'H_given_A': r'$C_{sem}^{H \leftarrow A}$',
    'A_given_H': r'$C_{sem}^{A \leftarrow H}$',
}
FIGURE_NAMES_M2 = {
    'bidirectional_comparison_bars': 'bidirectional_comparison_bars.png',
    'directional_asymmetry_bars': 'directional_asymmetry_bars.png',
    'asymmetry_delta_line': 'asymmetry_delta_line.png',
    'pairwise_distribution_violin': 'pairwise_distribution_violin.png',
    'significance_heatmap': 'significance_heatmap.png',
    'bootstrap_ci_comparison': 'bootstrap_ci_comparison.png',
    'ipw_adjusted_asymmetry': 'ipw_adjusted_asymmetry.png',
}


@dataclass
class VisualizationConfig:
    """Configuration for visualization output."""
    figure_size: tuple = (12, 5)
    figure_size_wide: tuple = (18, 6)
    dpi: int = 150
    font_size_title: int = 14
    font_size_label: int = 11
    font_size_tick: int = 9
    ci_alpha: float = 0.3
    save_format: str = "png"
    figures_dir: str = "figures"
    figure_size_bidir: tuple = (12, 6)
    figure_size_heatmap: tuple = (10, 6)
    figure_size_violin: tuple = (12, 6)


def get_figure_path(figures_dir: str, plot_type: str, model_slug: Optional[str] = None) -> str:
    """Construct figure output path.

    Args:
        figures_dir: Directory to save figures.
        plot_type: Plot type identifier (e.g., "tier_csem_bars").
        model_slug: Optional model slug (e.g., "minilm").

    Returns:
        Full path to figure file.
    """
    os.makedirs(figures_dir, exist_ok=True)
    if model_slug:
        return os.path.join(figures_dir, f"{plot_type}_{model_slug}.png")
    return os.path.join(figures_dir, f"{plot_type}.png")
from scipy.stats import gaussian_kde
from typing import Dict


def _ensure_figures_dir(figures_dir: str) -> None:
    os.makedirs(figures_dir, exist_ok=True)


def plot_gate_metrics(results: Dict, figures_dir: str) -> None:
    """Two-panel figure: C_sem bar with CI + grouped cosine bars.

    Left: C_sem bar with error bar (CI) + dashed zero line.
    Right: Three grouped bars for actual/topic/random cosine means.
    Colors: actual=blue, topic=orange, random=grey, C_sem=green.
    """
    _ensure_figures_dir(figures_dir)

    c_sem = results["c_sem"]
    c_sem_ci = results["c_sem_ci"]
    cos_actual = results["cos_actual_mean"]
    cos_topic = results["cos_topic_mean"]
    cos_random = results["cos_random_mean"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Left panel: C_sem with CI
    ci_lower = float(c_sem) - float(c_sem_ci[0])
    ci_upper = float(c_sem_ci[1]) - float(c_sem)
    ax1.bar(["C_sem"], [c_sem], color="green", alpha=0.7, width=0.4)
    ax1.errorbar(
        ["C_sem"], [c_sem],
        yerr=[[ci_lower], [ci_upper]],
        fmt="none", color="black", capsize=8, linewidth=2
    )
    ax1.axhline(0, color="black", linestyle="--", linewidth=1.5)
    ax1.set_ylabel("C_sem")
    ax1.set_title("Semantic Accommodation Index (C_sem)")
    text_y = float(c_sem) * 1.1 if abs(float(c_sem)) > 1e-6 else 0.001
    ax1.text(0, text_y, f"C_sem={c_sem:.4f}", ha="center", fontsize=10)

    # Right panel: grouped cosine similarity bars
    categories = ["cos_actual", "cos_topic", "cos_random"]
    values = [cos_actual, cos_topic, cos_random]
    colors = ["blue", "orange", "grey"]
    bars = ax2.bar(categories, values, color=colors, alpha=0.7)
    ax2.set_ylabel("Mean Cosine Similarity")
    ax2.set_title("Cosine Similarities by Condition")
    for bar, val in zip(bars, values):
        ax2.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.001,
            f"{val:.4f}", ha="center", va="bottom", fontsize=9
        )

    plt.tight_layout()
    path = os.path.join(figures_dir, "gate_metrics.png")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_partner_specificity(results: Dict, figures_dir: str) -> None:
    """Bar chart of 3 cosine similarity levels."""
    _ensure_figures_dir(figures_dir)

    categories = ["Actual (A_t)", "Topic-matched", "Random shuffle"]
    values = [
        results["cos_actual_mean"],
        results["cos_topic_mean"],
        results["cos_random_mean"],
    ]
    colors = ["blue", "orange", "grey"]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(categories, values, color=colors, alpha=0.8)
    ax.set_ylabel("Mean Cosine Similarity with H_{t+1}")
    ax.set_title("Partner Specificity: Cosine Similarity Levels")
    for bar, val in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.001,
            f"{val:.4f}", ha="center", va="bottom", fontsize=10
        )

    plt.tight_layout()
    path = os.path.join(figures_dir, "partner_specificity.png")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_bootstrap_dist(bootstrap_samples: np.ndarray, figures_dir: str) -> None:
    """Histogram of bootstrap C_sem distribution."""
    _ensure_figures_dir(figures_dir)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(bootstrap_samples, bins=50, color="green", alpha=0.7, edgecolor="white")
    ax.axvline(0, color="red", linestyle="--", linewidth=2, label="Zero")
    ax.axvline(
        np.percentile(bootstrap_samples, 2.5),
        color="orange", linestyle="--", linewidth=1.5, label="95% CI"
    )
    ax.axvline(
        np.percentile(bootstrap_samples, 97.5),
        color="orange", linestyle="--", linewidth=1.5
    )
    ax.set_xlabel("Bootstrap C_sem")
    ax.set_ylabel("Count")
    ax.set_title("Bootstrap Distribution of C_sem")
    ax.legend()

    plt.tight_layout()
    path = os.path.join(figures_dir, "bootstrap_dist.png")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_cosine_distributions(
    cos_actual: np.ndarray,
    cos_topic: np.ndarray,
    cos_random: np.ndarray,
    figures_dir: str,
) -> None:
    """KDE overlay of cosine similarity distributions."""
    _ensure_figures_dir(figures_dir)

    fig, ax = plt.subplots(figsize=(8, 5))
    for arr, color, label in [
        (cos_actual, "blue", "Actual"),
        (cos_topic, "orange", "Topic-matched"),
        (cos_random, "grey", "Random"),
    ]:
        try:
            kde = gaussian_kde(arr)
            x_range = np.linspace(arr.min() - 0.1, arr.max() + 0.1, 200)
            ax.plot(x_range, kde(x_range), color=color, label=label, linewidth=2)
            ax.fill_between(x_range, kde(x_range), alpha=0.2, color=color)
        except Exception:
            ax.hist(arr, bins=50, color=color, alpha=0.4, label=label, density=True)

    ax.set_xlabel("Cosine Similarity")
    ax.set_ylabel("Density")
    ax.set_title("Distribution of Cosine Similarities")
    ax.legend()

    plt.tight_layout()
    path = os.path.join(figures_dir, "cosine_distributions.png")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_residualization_check(
    cos_dict_before: Dict,
    cos_dict_after: Dict,
    figures_dir: str,
) -> None:
    """Before/after residualization scatter for cos_actual."""
    _ensure_figures_dir(figures_dir)

    before = cos_dict_before.get("cos_actual", np.array([]))
    after = cos_dict_after.get("cos_actual", np.array([]))

    if len(before) == 0 or len(after) == 0:
        return

    # Sample up to 2000 points for plot readability
    n = min(len(before), 2000)
    idx = np.random.choice(len(before), n, replace=False)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    ax1.scatter(before[idx], after[idx], alpha=0.3, s=5, color="blue")
    ax1.set_xlabel("Before Residualization")
    ax1.set_ylabel("After Residualization")
    ax1.set_title("Cos_actual: Before vs After Residualization")

    ax2.hist(before[idx], bins=50, alpha=0.5, label="Before", color="blue")
    ax2.hist(after[idx], bins=50, alpha=0.5, label="After", color="orange")
    ax2.set_xlabel("Cosine Similarity")
    ax2.set_ylabel("Count")
    ax2.set_title("Distribution Change from Residualization")
    ax2.legend()

    plt.tight_layout()
    path = os.path.join(figures_dir, "residualization_check.png")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_knn_quality(prompt_embeddings: np.ndarray, figures_dir: str) -> None:
    """KNN quality visualization: distribution of nearest neighbor distances."""
    _ensure_figures_dir(figures_dir)

    from sklearn.neighbors import NearestNeighbors

    # Sample for speed
    n = min(len(prompt_embeddings), 2000)
    idx = np.random.choice(len(prompt_embeddings), n, replace=False)
    sample = prompt_embeddings[idx]

    nn = NearestNeighbors(n_neighbors=6, metric="cosine", n_jobs=1)
    nn.fit(sample)
    distances, _ = nn.kneighbors(sample)

    # distances[:, 0] is self (0), use 1: for actual neighbors
    neighbor_dists = distances[:, 1:].flatten()

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(neighbor_dists, bins=50, color="purple", alpha=0.7)
    ax.set_xlabel("Cosine Distance to Nearest Neighbor")
    ax.set_ylabel("Count")
    ax.set_title(f"KNN Quality (k=5, n={n} samples)\nMean dist={neighbor_dists.mean():.4f}")

    plt.tight_layout()
    path = os.path.join(figures_dir, "knn_quality.png")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()


# ============================================================================
# H-M1 Visualization Suite: 7 Tier-Comparison Plot Functions
# ============================================================================

def plot_tier_csem_bars(all_model_results: Dict, figures_dir: str) -> None:
    """FR-V1 MANDATORY: Bar chart of C_sem per tier for each model.

    3 subplots (one per model), bars per tier, error bars from bootstrap CI.
    Annotates J-T p-value per subplot.

    Args:
        all_model_results: {model_slug: {tier_results, jt}}
        figures_dir: Directory to save figure (positional arg).
    """
    os.makedirs(figures_dir, exist_ok=True)
    model_slugs = list(all_model_results.keys())
    n_models = len(model_slugs)

    fig, axes = plt.subplots(1, n_models, figsize=(6 * n_models, 5), sharey=True)
    if n_models == 1:
        axes = [axes]

    for ax, slug in zip(axes, model_slugs):
        model_data = all_model_results[slug]
        tier_results = model_data.get("tier_results", {})
        jt = model_data.get("jt", {})
        jt_p = jt.get("jt_pvalue", 1.0)

        c_sems = []
        ci_lowers = []
        ci_uppers = []
        colors = []
        labels = []

        for tier in TIER_ORDER:
            if tier not in tier_results:
                continue
            tr = tier_results[tier]
            c_sem = tr.get("c_sem", 0.0)
            ci = tr.get("c_sem_ci", np.array([c_sem - 0.01, c_sem + 0.01]))
            c_sems.append(c_sem)
            ci_lowers.append(c_sem - ci[0])
            ci_uppers.append(ci[1] - c_sem)
            colors.append(TIER_COLORS[tier])
            labels.append(TIER_LABELS[tier])

        x = np.arange(len(c_sems))
        bars = ax.bar(x, c_sems, color=colors, alpha=0.8, edgecolor="black")
        ax.errorbar(x, c_sems,
                    yerr=[ci_lowers, ci_uppers],
                    fmt="none", color="black", capsize=5, linewidth=1.5)
        ax.axhline(0, color="gray", linestyle="--", linewidth=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=15, ha="right", fontsize=8)
        ax.set_title(f"{MODEL_DISPLAY_NAMES.get(slug, slug)}\nJ-T p={jt_p:.4f}", fontsize=11)
        ax.set_ylabel("C_sem" if slug == model_slugs[0] else "")

    plt.suptitle("C_sem per RLHF Tier by Model", fontsize=13, y=1.02)
    plt.tight_layout()
    path = os.path.join(figures_dir, "tier_csem_bars.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_tier_monotonicity_lines(all_model_results: Dict, figures_dir: str) -> None:
    """Line plot of C_sem across 3 tiers for each model.

    Args:
        all_model_results: {model_slug: {tier_results, jt}}
        figures_dir: Directory to save figure (positional arg).
    """
    os.makedirs(figures_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5))

    for slug, model_data in all_model_results.items():
        tier_results = model_data.get("tier_results", {})
        c_sems = [tier_results.get(t, {}).get("c_sem", 0.0) for t in TIER_ORDER]
        x = np.arange(len(TIER_ORDER))
        ax.plot(x, c_sems, marker="o", label=MODEL_DISPLAY_NAMES.get(slug, slug), linewidth=2)

    ax.set_xticks(np.arange(len(TIER_ORDER)))
    ax.set_xticklabels([TIER_LABELS[t] for t in TIER_ORDER], rotation=10)
    ax.axhline(0, color="gray", linestyle="--", linewidth=0.8)
    ax.set_ylabel("C_sem")
    ax.set_title("C_sem Monotonicity Across RLHF Tiers")
    ax.legend()
    plt.tight_layout()
    path = os.path.join(figures_dir, "tier_monotonicity_lines.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_cohend_heatmap(pairwise_results: Dict, figures_dir: str) -> None:
    """Heatmap of Cohen's d for all tier pairs × models.

    Color threshold at d=0.1 (minimum effect size threshold).

    Args:
        pairwise_results: {model_slug: {pair_key: {cohen_d, ...}}}
        figures_dir: Directory to save figure (positional arg).
    """
    os.makedirs(figures_dir, exist_ok=True)
    model_slugs = list(pairwise_results.keys())
    if not model_slugs:
        return

    # Get pair keys from first model
    pair_keys = list(pairwise_results[model_slugs[0]].keys())
    matrix = np.array([
        [abs(pairwise_results[slug].get(pk, {}).get("cohen_d", 0.0)) for pk in pair_keys]
        for slug in model_slugs
    ])

    fig, ax = plt.subplots(figsize=(10, 4))
    im = ax.imshow(matrix, cmap="YlOrRd", aspect="auto", vmin=0)
    ax.set_xticks(np.arange(len(pair_keys)))
    ax.set_xticklabels([pk.replace("helpful-", "").replace("-", " ") for pk in pair_keys],
                       rotation=30, ha="right", fontsize=8)
    ax.set_yticks(np.arange(len(model_slugs)))
    ax.set_yticklabels([MODEL_DISPLAY_NAMES.get(s, s) for s in model_slugs])
    plt.colorbar(im, ax=ax, label="Cohen's d")
    ax.set_title("Cohen's d Heatmap: Tier Pairs × Models (threshold d=0.1)")
    plt.tight_layout()
    path = os.path.join(figures_dir, "cohend_heatmap.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_tier_violin(tier_results: Dict, primary_model: str, figures_dir: str) -> None:
    """Violin plot of raw cosine similarities per tier.

    Args:
        tier_results: {tier_name: {raw_cos_actual: ndarray}}
        primary_model: Name/slug of primary model for title.
        figures_dir: Directory to save figure (positional arg).
    """
    os.makedirs(figures_dir, exist_ok=True)
    data = []
    labels = []
    colors = []

    for tier in TIER_ORDER:
        if tier not in tier_results:
            continue
        arr = tier_results[tier].get("raw_cos_actual", np.array([]))
        if len(arr) > 0:
            data.append(arr.tolist())
            labels.append(TIER_LABELS[tier])
            colors.append(TIER_COLORS[tier])

    if not data:
        return

    fig, ax = plt.subplots(figsize=(10, 5))
    parts = ax.violinplot(data, positions=np.arange(len(data)), showmedians=True)
    for i, (pc, color) in enumerate(zip(parts["bodies"], colors)):
        pc.set_facecolor(color)
        pc.set_alpha(0.7)
    ax.set_xticks(np.arange(len(labels)))
    ax.set_xticklabels(labels, rotation=10)
    ax.set_ylabel("Cosine Similarity (Raw)")
    ax.set_title(f"Raw Cosine Distribution per Tier\n({primary_model})")
    plt.tight_layout()
    path = os.path.join(figures_dir, "tier_violin.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_bootstrap_kde_tiers(tier_results: Dict, primary_model: str, figures_dir: str) -> None:
    """KDE of bootstrap C_sem per tier.

    Args:
        tier_results: {tier_name: {raw_cos_actual, raw_cos_random, c_sem_ci}}
        primary_model: Model slug for title.
        figures_dir: Directory to save figure (positional arg).
    """
    os.makedirs(figures_dir, exist_ok=True)
    from scipy.stats import gaussian_kde

    fig, ax = plt.subplots(figsize=(10, 5))

    for tier in TIER_ORDER:
        if tier not in tier_results:
            continue
        tr = tier_results[tier]
        cos_a = tr.get("raw_cos_actual", np.array([]))
        cos_r = tr.get("raw_cos_random", np.array([]))
        if len(cos_a) < 50:
            continue

        # Bootstrap C_sem distribution
        rng = np.random.default_rng(42)
        n = len(cos_a)
        boot = [np.mean(cos_a[rng.integers(0, n, n)]) - np.mean(cos_r[rng.integers(0, n, n)])
                for _ in range(500)]
        boot = np.array(boot)

        try:
            kde = gaussian_kde(boot)
            x = np.linspace(boot.min() - 0.005, boot.max() + 0.005, 200)
            ax.plot(x, kde(x), color=TIER_COLORS[tier],
                    label=TIER_LABELS[tier], linewidth=2)
            ax.fill_between(x, kde(x), alpha=0.2, color=TIER_COLORS[tier])
        except Exception:
            ax.hist(boot, bins=30, alpha=0.4, color=TIER_COLORS[tier], label=TIER_LABELS[tier])

    ax.axvline(0, color="gray", linestyle="--", linewidth=1)
    ax.set_xlabel("Bootstrap C_sem")
    ax.set_ylabel("Density")
    ax.set_title(f"Bootstrap C_sem KDE per Tier\n({primary_model})")
    ax.legend()
    plt.tight_layout()
    path = os.path.join(figures_dir, "bootstrap_kde_tiers.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_ipw_comparison(raw_csem: Dict, ipw_csem: Dict, figures_dir: str) -> None:
    """Compare raw vs IPW-adjusted C_sem per tier.

    Only generated if KS test triggered IPW correction.

    Args:
        raw_csem: {tier_name: raw_c_sem_float}
        ipw_csem: {tier_name: ipw_c_sem_float}
        figures_dir: Directory to save figure (positional arg).
    """
    os.makedirs(figures_dir, exist_ok=True)
    tiers = [t for t in TIER_ORDER if t in raw_csem and t in ipw_csem]
    if not tiers:
        return

    x = np.arange(len(tiers))
    raw_vals = [raw_csem[t] for t in tiers]
    ipw_vals = [ipw_csem[t] for t in tiers]
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x - width/2, raw_vals, width, label="Raw C_sem", alpha=0.8, color="#4878CF")
    ax.bar(x + width/2, ipw_vals, width, label="IPW C_sem", alpha=0.8, color="#D65F5F")
    ax.axhline(0, color="gray", linestyle="--")
    ax.set_xticks(x)
    ax.set_xticklabels([TIER_LABELS[t] for t in tiers], rotation=10)
    ax.set_ylabel("C_sem")
    ax.set_title("Raw vs IPW-Adjusted C_sem per Tier")
    ax.legend()
    plt.tight_layout()
    path = os.path.join(figures_dir, "ipw_comparison.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_ks_summary(ks_results: Dict, figures_dir: str) -> None:
    """Bar chart of KS statistics for tier pair comparisons.

    Args:
        ks_results: {pair_key: {ks_statistic, ks_pvalue, ipw_triggered}}
        figures_dir: Directory to save figure (positional arg).
    """
    os.makedirs(figures_dir, exist_ok=True)
    if not ks_results:
        return

    pair_keys = list(ks_results.keys())
    ks_stats = [ks_results[k]["ks_statistic"] for k in pair_keys]
    colors = ["#D65F5F" if ks_results[k]["ipw_triggered"] else "#4878CF" for k in pair_keys]

    fig, ax = plt.subplots(figsize=(8, 4))
    x = np.arange(len(pair_keys))
    ax.bar(x, ks_stats, color=colors, alpha=0.8, edgecolor="black")
    ax.set_xticks(x)
    ax.set_xticklabels(
        [k.replace("helpful-", "").replace("-", " ") for k in pair_keys],
        rotation=20, ha="right", fontsize=8
    )
    ax.set_ylabel("KS Statistic")
    ax.set_title("KS Test Statistics: Tier Prompt Distribution Overlap\n(Red = IPW triggered)")
    plt.tight_layout()
    path = os.path.join(figures_dir, "ks_summary.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()


# ============================================================================
# H-M2 EXTENSIONS: Bidirectional visualization functions
# ============================================================================

def plot_bidirectional_bars(all_model_results: Dict, figures_dir: str) -> None:
    """Grouped bar: C_sem^H<-A vs C_sem^A<-H per tier (REQUIRED primary figure)."""
    _ensure_figures_dir(figures_dir)
    n_tiers = len(TIER_ORDER)
    x = np.arange(n_tiers)
    width = 0.35

    # Average across models
    csem_H = []
    csem_A = []
    for tier in TIER_ORDER:
        h_vals = []
        a_vals = []
        for slug, model_data in all_model_results.items():
            tier_data = model_data.get("tier_results", model_data)
            if tier in tier_data:
                h_vals.append(tier_data[tier].get("csem_H_given_A", 0.0))
                a_vals.append(tier_data[tier].get("csem_A_given_H", 0.0))
        csem_H.append(float(np.mean(h_vals)) if h_vals else 0.0)
        csem_A.append(float(np.mean(a_vals)) if a_vals else 0.0)

    fig, ax = plt.subplots(figsize=(12, 6))
    bars1 = ax.bar(x - width/2, csem_H, width, label=DIRECTION_LABELS['H_given_A'],
                   color=DIRECTION_COLORS['H_given_A'], alpha=0.8, edgecolor='black')
    bars2 = ax.bar(x + width/2, csem_A, width, label=DIRECTION_LABELS['A_given_H'],
                   color=DIRECTION_COLORS['A_given_H'], alpha=0.8, edgecolor='black')
    ax.set_xticks(x)
    ax.set_xticklabels([TIER_LABELS.get(t, t) for t in TIER_ORDER], rotation=20, ha='right')
    ax.set_ylabel('C_sem (mean across models)')
    ax.set_title('Bidirectional Semantic Accommodation: H←A vs A←H')
    ax.axhline(0, color='gray', linestyle='--', linewidth=0.8)
    ax.legend()
    plt.tight_layout()
    path = os.path.join(figures_dir, FIGURE_NAMES_M2['bidirectional_comparison_bars'])
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_directional_asymmetry_bars(all_model_results: Dict, figures_dir: str) -> None:
    """3 models x 3 tiers x 2 direction bars."""
    _ensure_figures_dir(figures_dir)
    n_models = len(all_model_results)
    n_tiers = len(TIER_ORDER)
    fig, axes = plt.subplots(1, n_models, figsize=(12, 6), sharey=True)
    if n_models == 1:
        axes = [axes]
    for ax, (slug, model_data) in zip(axes, all_model_results.items()):
        tier_data = model_data.get("tier_results", model_data)
        x = np.arange(n_tiers)
        width = 0.35
        csem_H = [tier_data.get(t, {}).get("csem_H_given_A", 0.0) for t in TIER_ORDER]
        csem_A = [tier_data.get(t, {}).get("csem_A_given_H", 0.0) for t in TIER_ORDER]
        ax.bar(x - width/2, csem_H, width, color=DIRECTION_COLORS['H_given_A'], alpha=0.8)
        ax.bar(x + width/2, csem_A, width, color=DIRECTION_COLORS['A_given_H'], alpha=0.8)
        ax.set_title(MODEL_DISPLAY_NAMES.get(slug, slug))
        ax.set_xticks(x)
        ax.set_xticklabels(['T1', 'T2', 'T3'])
        ax.axhline(0, color='gray', linestyle='--', linewidth=0.8)
    axes[0].set_ylabel('C_sem')
    plt.suptitle('Directional Asymmetry by Model')
    plt.tight_layout()
    path = os.path.join(figures_dir, FIGURE_NAMES_M2['directional_asymmetry_bars'])
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_asymmetry_delta_line(all_model_results: Dict, figures_dir: str) -> None:
    """Delta_asymmetry = C_sem^H<-A - C_sem^A<-H across tiers per model."""
    _ensure_figures_dir(figures_dir)
    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(TIER_ORDER))
    for slug, model_data in all_model_results.items():
        tier_data = model_data.get("tier_results", model_data)
        deltas = [
            tier_data.get(t, {}).get("csem_H_given_A", 0.0) - tier_data.get(t, {}).get("csem_A_given_H", 0.0)
            for t in TIER_ORDER
        ]
        ax.plot(x, deltas, marker='o', label=MODEL_DISPLAY_NAMES.get(slug, slug))
    ax.set_xticks(x)
    ax.set_xticklabels([TIER_LABELS.get(t, t) for t in TIER_ORDER], rotation=20, ha='right')
    ax.set_ylabel('Δ_asymmetry (H←A minus A←H)')
    ax.set_title('Asymmetry Delta Across Tiers')
    ax.axhline(0, color='gray', linestyle='--', linewidth=0.8)
    ax.legend()
    plt.tight_layout()
    path = os.path.join(figures_dir, FIGURE_NAMES_M2['asymmetry_delta_line'])
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_pairwise_distributions_violin(all_model_results: Dict, figures_dir: str) -> None:
    """Violin/KDE per-pair C_sem both directions."""
    _ensure_figures_dir(figures_dir)
    fig, ax = plt.subplots(figsize=(12, 6))
    positions = []
    data_h = []
    data_a = []
    labels = []
    for i, tier in enumerate(TIER_ORDER):
        for slug, model_data in all_model_results.items():
            tier_data = model_data.get("tier_results", model_data)
            if tier in tier_data:
                arr_h = tier_data[tier].get("csem_H_given_A_array", np.array([0.0]))
                arr_a = tier_data[tier].get("csem_A_given_H_array", np.array([0.0]))
                if len(arr_h) > 0:
                    data_h.append(arr_h[:500] if len(arr_h) > 500 else arr_h)
                    data_a.append(arr_a[:500] if len(arr_a) > 500 else arr_a)
                    labels.append(f"{TIER_LABELS.get(tier, tier)}\n{MODEL_DISPLAY_NAMES.get(slug, slug)}")
    if data_h:
        positions_h = np.arange(1, len(data_h) * 2, 2)
        positions_a = np.arange(2, len(data_a) * 2 + 1, 2)
        vp1 = ax.violinplot(data_h, positions=positions_h, showmedians=True)
        vp2 = ax.violinplot(data_a, positions=positions_a, showmedians=True)
        for pc in vp1['bodies']:
            pc.set_facecolor(DIRECTION_COLORS['H_given_A'])
            pc.set_alpha(0.6)
        for pc in vp2['bodies']:
            pc.set_facecolor(DIRECTION_COLORS['A_given_H'])
            pc.set_alpha(0.6)
    ax.set_title('Per-pair C_sem Distributions: H←A vs A←H')
    ax.set_ylabel('C_sem per pair')
    plt.tight_layout()
    path = os.path.join(figures_dir, FIGURE_NAMES_M2['pairwise_distribution_violin'])
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_significance_heatmap(all_model_results: Dict, figures_dir: str) -> None:
    """p-value grid: tier x model heatmap."""
    _ensure_figures_dir(figures_dir)
    model_slugs = list(all_model_results.keys())
    pvals = np.ones((len(TIER_ORDER), len(model_slugs)))
    for j, slug in enumerate(model_slugs):
        model_data = all_model_results[slug]
        asym = model_data.get("asymmetry_test", {})
        for i, tier in enumerate(TIER_ORDER):
            if tier in asym:
                pvals[i, j] = asym[tier].get("p_value", 1.0)
    fig, ax = plt.subplots(figsize=(10, 6))
    im = ax.imshow(pvals, cmap='RdYlGn_r', vmin=0, vmax=0.1, aspect='auto')
    ax.set_xticks(np.arange(len(model_slugs)))
    ax.set_xticklabels([MODEL_DISPLAY_NAMES.get(s, s) for s in model_slugs])
    ax.set_yticks(np.arange(len(TIER_ORDER)))
    ax.set_yticklabels([TIER_LABELS.get(t, t) for t in TIER_ORDER])
    plt.colorbar(im, ax=ax, label='p-value')
    ax.set_title('Significance Heatmap: H←A > A←H (Mann-Whitney p-value)')
    for i in range(len(TIER_ORDER)):
        for j in range(len(model_slugs)):
            ax.text(j, i, f'{pvals[i,j]:.3f}', ha='center', va='center', fontsize=8,
                    color='white' if pvals[i,j] < 0.05 else 'black')
    plt.tight_layout()
    path = os.path.join(figures_dir, FIGURE_NAMES_M2['significance_heatmap'])
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_bootstrap_ci_comparison(all_model_results: Dict, figures_dir: str) -> None:
    """Bootstrap CI both directions per tier (averaged across models)."""
    _ensure_figures_dir(figures_dir)
    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(TIER_ORDER))
    width = 0.35
    means_h, means_a = [], []
    for tier in TIER_ORDER:
        h_vals, a_vals = [], []
        for slug, model_data in all_model_results.items():
            tier_data = model_data.get("tier_results", model_data)
            if tier in tier_data:
                h_vals.append(tier_data[tier].get("csem_H_given_A", 0.0))
                a_vals.append(tier_data[tier].get("csem_A_given_H", 0.0))
        means_h.append(float(np.mean(h_vals)) if h_vals else 0.0)
        means_a.append(float(np.mean(a_vals)) if a_vals else 0.0)
    ax.bar(x - width/2, means_h, width, label=DIRECTION_LABELS['H_given_A'],
           color=DIRECTION_COLORS['H_given_A'], alpha=0.8)
    ax.bar(x + width/2, means_a, width, label=DIRECTION_LABELS['A_given_H'],
           color=DIRECTION_COLORS['A_given_H'], alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([TIER_LABELS.get(t, t) for t in TIER_ORDER], rotation=20, ha='right')
    ax.set_ylabel('C_sem (mean)')
    ax.set_title('Bootstrap CI Comparison: Both Directions per Tier')
    ax.axhline(0, color='gray', linestyle='--')
    ax.legend()
    plt.tight_layout()
    path = os.path.join(figures_dir, FIGURE_NAMES_M2['bootstrap_ci_comparison'])
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_ipw_asymmetry(all_model_results: Dict, ipw_results: Dict, figures_dir: str) -> None:
    """Raw vs IPW-corrected delta_asymmetry."""
    _ensure_figures_dir(figures_dir)
    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(TIER_ORDER))
    raw_deltas = []
    ipw_deltas = []
    for tier in TIER_ORDER:
        raw_h, raw_a = [], []
        ipw_h, ipw_a = [], []
        for slug, model_data in all_model_results.items():
            tier_data = model_data.get("tier_results", model_data)
            if tier in tier_data:
                raw_h.append(tier_data[tier].get("csem_H_given_A", 0.0))
                raw_a.append(tier_data[tier].get("csem_A_given_H", 0.0))
        for slug, ipw_model in ipw_results.items():
            if tier in ipw_model:
                ipw_h.append(ipw_model[tier].get("ipw_csem_H_given_A", 0.0))
                ipw_a.append(ipw_model[tier].get("ipw_csem_A_given_H", 0.0))
        raw_deltas.append(float(np.mean(raw_h) - np.mean(raw_a)) if raw_h else 0.0)
        ipw_deltas.append(float(np.mean(ipw_h) - np.mean(ipw_a)) if ipw_h else 0.0)
    ax.plot(x, raw_deltas, marker='o', label='Raw Δ', color='#4878CF')
    ax.plot(x, ipw_deltas, marker='s', linestyle='--', label='IPW-adjusted Δ', color='#D65F5F')
    ax.set_xticks(x)
    ax.set_xticklabels([TIER_LABELS.get(t, t) for t in TIER_ORDER], rotation=20, ha='right')
    ax.set_ylabel('Δ_asymmetry')
    ax.set_title('Raw vs IPW-corrected Asymmetry')
    ax.axhline(0, color='gray', linestyle='--')
    ax.legend()
    plt.tight_layout()
    path = os.path.join(figures_dir, FIGURE_NAMES_M2['ipw_adjusted_asymmetry'])
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()


# ============================================================================
# H-M3 EXTENSIONS: 6 Figure Functions for Delta Analysis
# ============================================================================

def plot_delta_distributions(
    delta_results_by_op,
    save_path: str,
    config=None,
) -> None:
    """MANDATORY Fig 1: Violin plot of per-pair Δ distributions per operationalization.

    Args:
        delta_results_by_op: Dict[str, np.ndarray] - {"raw": [N,], "length_matched": [N,], "prompt_projected": [N,]}
        save_path: Full path to save the figure.
        config: Optional visualization config.
    """
    import seaborn as sns
    import pandas as pd

    data_rows = []
    op_labels = {"raw": "OP1 (Raw)", "length_matched": "OP2 (Length-Matched)", "prompt_projected": "OP3 (Proj.)"}
    for op, deltas in delta_results_by_op.items():
        for v in np.asarray(deltas).flatten():
            data_rows.append({"Operationalization": op_labels.get(op, op), "Δ": float(v)})

    df = pd.DataFrame(data_rows)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.violinplot(data=df, x="Operationalization", y="Δ", ax=ax, inner="box", cut=0)
    ax.axhline(0, color="red", linestyle="--", linewidth=1, label="Δ=0")
    ax.set_title("Δ = cos(H_next, A_chosen) - cos(H_next, A_rejected)\nPer Operationalization")
    ax.set_ylabel("Delta (per pair)")
    ax.legend()
    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else ".", exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_bootstrap_ci_by_op_and_model(
    all_model_op_stats,
    save_path: str,
    config=None,
) -> None:
    """MANDATORY Fig 2: E[Δ] ± 95% CI grouped bar chart by op and model.

    Args:
        all_model_op_stats: Dict[model_slug, Dict[op, {mean_delta, ci_lower, ci_upper}]]
        save_path: Full path to save the figure.
        config: Optional visualization config.
    """
    ops = ["raw", "length_matched", "prompt_projected"]
    op_labels = ["OP1 (Raw)", "OP2 (Len.)", "OP3 (Proj.)"]
    models = list(all_model_op_stats.keys())

    x = np.arange(len(ops))
    width = 0.25
    fig, ax = plt.subplots(figsize=(12, 6))

    for i, model_slug in enumerate(models):
        op_data = all_model_op_stats[model_slug]
        means = [op_data.get(op, {}).get("mean_delta", 0.0) for op in ops]
        ci_lo = [op_data.get(op, {}).get("ci_lower", 0.0) for op in ops]
        ci_hi = [op_data.get(op, {}).get("ci_upper", 0.0) for op in ops]
        yerr_lo = [m - lo for m, lo in zip(means, ci_lo)]
        yerr_hi = [hi - m for m, hi in zip(means, ci_hi)]
        ax.bar(
            x + i * width, means, width,
            yerr=[yerr_lo, yerr_hi],
            label=model_slug, capsize=4, alpha=0.8
        )

    ax.axhline(0, color="red", linestyle="--", linewidth=1)
    ax.set_xticks(x + width)
    ax.set_xticklabels(op_labels)
    ax.set_ylabel("E[Δ] (± 95% CI)")
    ax.set_title("Bootstrap E[Δ] per Operationalization and Model")
    ax.legend()
    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else ".", exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_n_pairs_bar(
    tier_n_pairs,
    min_threshold: int,
    save_path: str,
    config=None,
) -> None:
    """MANDATORY Fig 3: N_pairs per tier with gate threshold horizontal line.

    Args:
        tier_n_pairs: Dict[str, int] - {tier_name: n_pairs}
        min_threshold: Gate threshold for N_pairs (e.g., 1000).
        save_path: Full path to save the figure.
        config: Optional visualization config.
    """
    tiers = list(tier_n_pairs.keys())
    counts = [tier_n_pairs[t] for t in tiers]
    tier_labels = [t.replace("helpful-", "").replace("-", "\n") for t in tiers]

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ["green" if c >= min_threshold else "red" for c in counts]
    ax.bar(tier_labels, counts, color=colors, alpha=0.8)
    ax.axhline(min_threshold, color="red", linestyle="--", linewidth=1.5,
               label=f"Min threshold ({min_threshold})")
    ax.set_ylabel("N_pairs")
    ax.set_title("Chosen/Rejected Pair Counts per RLHF Tier")
    ax.legend()
    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else ".", exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_delta_by_tier(
    delta_results_by_tier_op,
    tier_order,
    save_path: str,
    config=None,
) -> None:
    """AUTONOMOUS Fig 4: E[Δ] by RLHF tier for each operationalization.

    Args:
        delta_results_by_tier_op: Dict[tier, Dict[op, np.ndarray]]
        tier_order: List[str] of tier names in order.
        save_path: Full path to save the figure.
        config: Optional visualization config.
    """
    ops = ["raw", "length_matched", "prompt_projected"]
    op_labels = ["OP1 (Raw)", "OP2 (Len.)", "OP3 (Proj.)"]
    tier_labels = [t.replace("helpful-", "").replace("-", "\n") for t in tier_order]

    fig, ax = plt.subplots(figsize=(10, 6))
    for op, op_label in zip(ops, op_labels):
        means = [
            float(np.mean(delta_results_by_tier_op.get(t, {}).get(op, [0.0])))
            for t in tier_order
        ]
        ax.plot(tier_labels, means, marker="o", label=op_label)

    ax.axhline(0, color="gray", linestyle="--", linewidth=0.8)
    ax.set_ylabel("E[Δ]")
    ax.set_title("E[Δ] by RLHF Tier per Operationalization")
    ax.legend()
    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else ".", exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_delta_raw_vs_length_scatter(
    delta_raw: np.ndarray,
    delta_length: np.ndarray,
    save_path: str,
    config=None,
) -> None:
    """AUTONOMOUS Fig 5: Scatter OP1 (raw) vs OP2 (length-matched) per pair.

    Args:
        delta_raw: [N,] OP1 delta values.
        delta_length: [N,] OP2 delta values.
        save_path: Full path to save the figure.
        config: Optional visualization config.
    """
    # Sample at most 5000 points for scatter legibility
    n = len(delta_raw)
    if n > 5000:
        rng = np.random.default_rng(42)
        idx = rng.choice(n, size=5000, replace=False)
        delta_raw = delta_raw[idx]
        delta_length = delta_length[idx]

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.scatter(delta_raw, delta_length, alpha=0.3, s=5, c="steelblue")
    lim = max(abs(delta_raw).max(), abs(delta_length).max()) * 1.1
    ax.plot([-lim, lim], [-lim, lim], "k--", linewidth=0.8, label="y=x")
    ax.axhline(0, color="gray", linewidth=0.5)
    ax.axvline(0, color="gray", linewidth=0.5)
    ax.set_xlabel("OP1 Δ (raw)")
    ax.set_ylabel("OP2 Δ (length-matched)")
    ax.set_title("OP1 vs OP2 Δ per Pair (n≤5000 sample)")
    ax.legend()
    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else ".", exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_model_op_heatmap(
    summary_matrix,
    model_names,
    save_path: str,
    config=None,
) -> None:
    """AUTONOMOUS Fig 6: 3-model x 3-op heatmap of mean_delta values.

    Args:
        summary_matrix: Dict[model_slug, Dict[op, mean_delta]]
        model_names: List[str] of model slugs.
        save_path: Full path to save the figure.
        config: Optional visualization config.
    """
    import seaborn as sns
    import pandas as pd

    ops = ["raw", "length_matched", "prompt_projected"]
    op_labels = ["OP1 (Raw)", "OP2 (Len.)", "OP3 (Proj.)"]
    data = []
    for model in model_names:
        row = [summary_matrix.get(model, {}).get(op, 0.0) for op in ops]
        data.append(row)

    df_heat = pd.DataFrame(data, index=model_names, columns=op_labels)
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.heatmap(df_heat, annot=True, fmt=".4f", cmap="RdYlGn", center=0, ax=ax)
    ax.set_title("Mean Δ Heatmap: Model × Operationalization")
    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else ".", exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
