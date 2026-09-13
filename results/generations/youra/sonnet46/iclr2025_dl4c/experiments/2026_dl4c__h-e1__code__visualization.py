"""Visualization functions for h-e1 prescreening results."""
import os
import logging
import numpy as np

logger = logging.getLogger(__name__)


def plot_gate_metrics(
    metrics: dict,
    thresholds: dict,
    output_path: str,
) -> None:
    """Bar chart of gate metrics vs thresholds.

    Args:
        metrics: output of compute_gate_metrics().
        thresholds: dict with 'fraction_k_pass_ge1' and 'pct_groups_above_1_5x' keys.
        output_path: path to save figure.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 5))

    metric_names = ["fraction_k_pass_ge1", "pct_groups_above_1_5x"]
    labels = ["Fraction k-pass ≥ 1", "% Groups above 1.5x VR"]
    values = [metrics.get(m, 0.0) for m in metric_names]
    thresh_values = [thresholds.get(m, None) for m in metric_names]

    x = np.arange(len(labels))
    bars = ax.bar(x, values, color=["steelblue", "darkorange"], alpha=0.8, label="Observed")

    for i, tv in enumerate(thresh_values):
        if tv is not None:
            ax.axhline(y=tv, xmin=(i / len(labels)), xmax=((i + 1) / len(labels)),
                       color="red", linestyle="--", linewidth=2)

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 1.1)
    ax.set_ylabel("Value")
    ax.set_title(
        f"Gate Metrics — {'PASS' if metrics.get('gate_pass') else 'FAIL'}\n"
        f"n_problems={metrics.get('n_problems', 0)}, "
        f"mean_var_ratio={metrics.get('mean_var_ratio', 0.0):.3f}"
    )

    # Add value labels on bars
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                f"{val:.3f}", ha="center", va="bottom", fontsize=10)

    ax.legend(["Threshold", "Observed"], loc="upper right")
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()
    logger.info(f"Saved gate metrics figure to {output_path}")


def plot_s_term_distribution(
    s_terms_all: list[float],
    s_terms_filtered: list[float],
    output_path: str,
) -> None:
    """Histogram of S_term values, showing all vs prescreened.

    Args:
        s_terms_all: S_term values for all evaluated problems.
        s_terms_filtered: S_term values after [0.3, 0.55] filter.
        output_path: path to save figure.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 5))

    bins = np.linspace(0, 1, 21)
    ax.hist(s_terms_all, bins=bins, alpha=0.5, color="steelblue", label=f"All (n={len(s_terms_all)})")
    ax.hist(s_terms_filtered, bins=bins, alpha=0.7, color="darkorange",
            label=f"Prescreened (n={len(s_terms_filtered)})")

    ax.axvline(x=0.3, color="red", linestyle="--", linewidth=1.5, label="S_term=0.3")
    ax.axvline(x=0.55, color="red", linestyle="--", linewidth=1.5, label="S_term=0.55")

    ax.set_xlabel("S_term (fraction of rollouts passing ≥1 test)")
    ax.set_ylabel("Count")
    ax.set_title("S_term Distribution")
    ax.legend()
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()
    logger.info(f"Saved S_term distribution figure to {output_path}")


def plot_variance_ratio_scatter(
    per_problem_results: list[dict],
    output_path: str,
) -> None:
    """Scatter plot of var(R_ratio) vs var(R_binary) per problem.

    Args:
        per_problem_results: list of dicts with r_ratio_vec and r_binary_vec.
        output_path: path to save figure.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import json

    var_ratios = []
    var_binaries = []

    for row in per_problem_results:
        r_ratio_vec = row.get("r_ratio_vec", [])
        r_binary_vec = row.get("r_binary_vec", [])
        if isinstance(r_ratio_vec, str):
            r_ratio_vec = json.loads(r_ratio_vec)
        if isinstance(r_binary_vec, str):
            r_binary_vec = json.loads(r_binary_vec)
        var_r = float(np.var(r_ratio_vec)) if r_ratio_vec else 0.0
        var_b = float(np.var(r_binary_vec)) if r_binary_vec else 0.0
        var_ratios.append(var_r)
        var_binaries.append(var_b)

    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(var_binaries, var_ratios, alpha=0.4, s=15, color="steelblue")

    max_val = max(max(var_binaries, default=0.25), max(var_ratios, default=0.25), 0.25)
    ax.plot([0, max_val], [0, max_val], "k--", linewidth=1, label="1:1")
    ax.plot([0, max_val], [0, 1.5 * max_val], "r--", linewidth=1, label="1.5x")

    ax.set_xlabel("var(R_binary)")
    ax.set_ylabel("var(R_ratio)")
    ax.set_title("Variance Scatter: R_ratio vs R_binary (per problem group)")
    ax.legend()
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()
    logger.info(f"Saved variance ratio scatter figure to {output_path}")


def plot_t_distribution(
    t_counts: list[int],
    output_path: str,
) -> None:
    """Histogram of T (number of test cases per problem).

    Args:
        t_counts: list of T values per problem.
        output_path: path to save figure.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 5))
    max_t = max(t_counts) if t_counts else 20
    bins = np.arange(0.5, max_t + 1.5, 1)
    ax.hist(t_counts, bins=bins, color="steelblue", alpha=0.8, edgecolor="white")
    ax.axvline(x=3, color="red", linestyle="--", linewidth=1.5, label="T=3 (min filter)")
    ax.set_xlabel("T (number of test cases)")
    ax.set_ylabel("Count")
    ax.set_title(f"Test Case Count Distribution (n={len(t_counts)} problems)")
    ax.legend()
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()
    logger.info(f"Saved T distribution figure to {output_path}")


def plot_empirical_vs_theoretical(
    per_problem_results: list[dict],
    output_path: str,
) -> None:
    """Plot empirical variance ratio CDF vs theoretical expectation.

    Args:
        per_problem_results: list of dicts with r_ratio_vec and r_binary_vec.
        output_path: path to save figure.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import json

    variance_ratios = []
    for row in per_problem_results:
        r_ratio_vec = row.get("r_ratio_vec", [])
        r_binary_vec = row.get("r_binary_vec", [])
        if isinstance(r_ratio_vec, str):
            r_ratio_vec = json.loads(r_ratio_vec)
        if isinstance(r_binary_vec, str):
            r_binary_vec = json.loads(r_binary_vec)
        if not r_ratio_vec or not r_binary_vec:
            continue
        var_r = float(np.var(r_ratio_vec))
        var_b = float(np.var(r_binary_vec))
        if var_b > 1e-8:
            variance_ratios.append(var_r / var_b)

    if not variance_ratios:
        logger.warning("No non-degenerate groups for empirical vs theoretical plot.")
        return

    variance_ratios_sorted = np.sort(variance_ratios)
    n = len(variance_ratios_sorted)
    empirical_cdf = np.arange(1, n + 1) / n

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(variance_ratios_sorted, empirical_cdf, label="Empirical CDF", color="steelblue")
    ax.axvline(x=1.5, color="red", linestyle="--", linewidth=1.5, label="Threshold 1.5x")
    ax.axvline(x=1.0, color="gray", linestyle=":", linewidth=1.0, label="Null (ratio=1)")

    ax.set_xlabel("Variance Ratio (var_ratio / var_binary)")
    ax.set_ylabel("CDF")
    ax.set_title(f"Empirical CDF of Variance Ratio (n={n} non-degenerate groups)")
    ax.legend()
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()
    logger.info(f"Saved empirical vs theoretical figure to {output_path}")


def generate_all_figures(
    metrics: dict,
    per_problem_results: list[dict],
    figures_dir: str,
) -> None:
    """Generate all 5 mandatory figures.

    Args:
        metrics: output of compute_gate_metrics().
        per_problem_results: list of per-problem result dicts.
        figures_dir: directory to save figures.
    """
    import json

    os.makedirs(figures_dir, exist_ok=True)

    # Figure 1: Gate metrics bar chart
    thresholds = {
        "fraction_k_pass_ge1": 0.10,
        "pct_groups_above_1_5x": 0.80,
    }
    plot_gate_metrics(
        metrics=metrics,
        thresholds=thresholds,
        output_path=os.path.join(figures_dir, "gate_metrics.png"),
    )

    # Figure 2: S_term distribution
    s_terms_all = [r.get("s_term", 0.0) for r in per_problem_results]
    s_terms_filtered = [s for s in s_terms_all if 0.3 <= s <= 0.55]
    plot_s_term_distribution(
        s_terms_all=s_terms_all,
        s_terms_filtered=s_terms_filtered,
        output_path=os.path.join(figures_dir, "s_term_distribution.png"),
    )

    # Figure 3: Variance ratio scatter
    plot_variance_ratio_scatter(
        per_problem_results=per_problem_results,
        output_path=os.path.join(figures_dir, "variance_ratio_scatter.png"),
    )

    # Figure 4: T distribution
    t_counts = [r.get("T", 0) for r in per_problem_results if r.get("T", 0) > 0]
    plot_t_distribution(
        t_counts=t_counts,
        output_path=os.path.join(figures_dir, "t_distribution.png"),
    )

    # Figure 5: Empirical vs theoretical CDF
    plot_empirical_vs_theoretical(
        per_problem_results=per_problem_results,
        output_path=os.path.join(figures_dir, "empirical_vs_theoretical.png"),
    )

    logger.info(f"All figures saved to {figures_dir}")
