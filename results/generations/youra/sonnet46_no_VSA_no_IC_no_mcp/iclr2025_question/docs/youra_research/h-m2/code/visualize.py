import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os


def plot_auroc_comparison(results: dict, out_path: str) -> None:
    """Bar chart: AUROC_clustered vs AUROC_ablated with 95% CI error bars."""
    fig, ax = plt.subplots(figsize=(6, 4))
    labels = ["SE_clustered", "Ablated (no NLI)"]
    aurocs = [results["auroc_clustered"], results["auroc_ablated"]]
    ci_lo = [results["ci_clustered"][0], results["ci_ablated"][0]]
    ci_hi = [results["ci_clustered"][1], results["ci_ablated"][1]]
    yerr = [[a - lo for a, lo in zip(aurocs, ci_lo)],
            [hi - a for a, hi in zip(aurocs, ci_hi)]]
    ax.bar(labels, aurocs, yerr=yerr, capsize=5, color=["steelblue", "coral"])
    ax.set_ylabel("AUROC")
    ax.set_ylim(0.4, 1.0)
    ax.set_title(f"AUROC Comparison  (ΔAUROC={results['delta_auroc']:.4f}, gate={'PASS' if results['gate_pass'] else 'FAIL'})")
    ax.axhline(0.5, color="gray", linestyle="--", alpha=0.5, label="Random")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_within_cluster_scatter(
    within_fracs: list,
    question_ids: list,
    subset_ids: list,
    out_path: str,
) -> None:
    """Scatter: within-cluster fraction vs question index; subset highlighted."""
    fig, ax = plt.subplots(figsize=(8, 4))
    subset_set = set(subset_ids)
    xs, ys, cs = [], [], []
    for i, (qid, frac) in enumerate(zip(question_ids, within_fracs)):
        xs.append(i)
        ys.append(frac)
        cs.append("red" if qid in subset_set else "steelblue")
    ax.scatter(xs, ys, c=cs, alpha=0.6, s=20)
    ax.set_xlabel("Question index")
    ax.set_ylabel("Within-cluster fraction")
    ax.set_title("Within-cluster fraction per question (red = paraphrase subset)")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_cluster_count_histogram(cluster_counts: list, out_path: str) -> None:
    """Histogram: cluster count distribution N=98."""
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(cluster_counts, bins=range(1, 12), align="left", rwidth=0.8, color="steelblue")
    ax.set_xlabel("Cluster count")
    ax.set_ylabel("Number of questions")
    ax.set_title("Distribution of cluster counts (N=98)")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_se_boxplot(
    se_clustered: list,
    within_fracs: list,
    out_path: str,
) -> None:
    """Box plot: SE (clustered) and within-cluster fraction side-by-side."""
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.boxplot([se_clustered, within_fracs], labels=["SE_clustered", "within_frac"])
    ax.set_ylabel("Value")
    ax.set_title("Distribution of SE and within-cluster fraction")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def generate_all_figures(
    results: dict,
    se_clustered: list,
    within_fracs: list,
    cluster_counts: list,
    question_ids: list,
    subset_ids: list,
    figures_dir: str,
) -> None:
    os.makedirs(figures_dir, exist_ok=True)
    plot_auroc_comparison(results, os.path.join(figures_dir, "auroc_comparison.png"))
    plot_within_cluster_scatter(within_fracs, question_ids, subset_ids,
                                os.path.join(figures_dir, "within_cluster_scatter.png"))
    plot_cluster_count_histogram(cluster_counts, os.path.join(figures_dir, "cluster_count_hist.png"))
    plot_se_boxplot(se_clustered, within_fracs, os.path.join(figures_dir, "se_boxplot.png"))
