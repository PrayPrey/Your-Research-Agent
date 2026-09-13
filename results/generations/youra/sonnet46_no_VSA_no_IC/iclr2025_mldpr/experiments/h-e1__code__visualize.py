from __future__ import annotations
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from config import CFG


def _save(fig: plt.Figure, path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {path}")


def plot_gate_metrics(results: dict, figures_dir: str) -> None:
    """fig1: bar chart of permutation_p vs 0.05, paper_count_star vs [10, 120]."""
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    p_val = results.get("permutation_p", 1.0)
    axes[0].bar(["Permutation p"], [p_val], color="steelblue")
    axes[0].axhline(0.05, color="red", linestyle="--", label="threshold=0.05")
    axes[0].set_ylim(0, max(p_val * 1.2, 0.1))
    axes[0].set_title("Permutation p-value")
    axes[0].legend()

    pcs = results.get("paper_count_star") or 0
    axes[1].bar(["paper_count*"], [pcs], color="darkorange")
    axes[1].axhspan(10, 120, alpha=0.2, color="green", label="valid range [10, 120]")
    axes[1].set_title("paper_count* vs valid range")
    axes[1].legend()

    fig.suptitle("Gate Metrics Summary")
    _save(fig, str(Path(figures_dir) / "fig1_gate_metrics.png"))


def plot_cov_scatter(
    paper_counts: np.ndarray,
    cov_values: np.ndarray,
    paper_count_star: float,
    ols_metrics: dict,
    figures_dir: str,
) -> None:
    """fig2: scatter + OLS line + vertical dashed line at paper_count*."""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(paper_counts, cov_values, alpha=0.5, s=20, label="benchmarks")

    x_line = np.linspace(paper_counts.min(), paper_counts.max(), 200)
    y_line = ols_metrics["slope"] * x_line + ols_metrics["intercept"]
    ax.plot(x_line, y_line, "r-", label=f"OLS (ρ={ols_metrics['rho']:.2f})")

    if paper_count_star is not None:
        ax.axvline(paper_count_star, color="purple", linestyle="--",
                   label=f"paper_count*={paper_count_star:.0f}")

    ax.set_xlabel("paper_count")
    ax.set_ylabel("result_CoV")
    ax.set_title("CoV vs paper_count with OLS trend")
    ax.legend()
    _save(fig, str(Path(figures_dir) / "fig2_cov_scatter.png"))


def plot_residual_series(
    sorted_paper_counts: np.ndarray,
    residual_cov: np.ndarray,
    breakpoint_idx: int,
    figures_dir: str,
) -> None:
    """fig3: residual CoV series with pre/post shading."""
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(sorted_paper_counts, residual_cov, "o-", ms=3, alpha=0.7)

    if breakpoint_idx is not None:
        bkp_pc = sorted_paper_counts[breakpoint_idx]
        ax.axvspan(sorted_paper_counts.min(), bkp_pc, alpha=0.1, color="blue", label="pre-break")
        ax.axvspan(bkp_pc, sorted_paper_counts.max(), alpha=0.1, color="orange", label="post-break")
        ax.axvline(bkp_pc, color="red", linestyle="--", label=f"paper_count*={bkp_pc:.0f}")

    ax.set_xlabel("paper_count (sorted)")
    ax.set_ylabel("residual CoV")
    ax.set_title("Residual CoV Series (OLS detrended)")
    ax.legend()
    _save(fig, str(Path(figures_dir) / "fig3_residual_series.png"))


def plot_permutation_null(
    null_distribution: np.ndarray,
    observed_bkp_idx: int,
    figures_dir: str,
) -> None:
    """fig4: histogram of null breakpoint positions + observed marked."""
    fig, ax = plt.subplots(figsize=(8, 4))
    if len(null_distribution) > 0:
        ax.hist(null_distribution, bins=30, color="steelblue", alpha=0.7, label="null distribution")
    if observed_bkp_idx is not None:
        ax.axvline(observed_bkp_idx, color="red", linestyle="--",
                   label=f"observed idx={observed_bkp_idx}")
    ax.set_xlabel("breakpoint index")
    ax.set_ylabel("count")
    ax.set_title("Permutation Null Distribution of Breakpoint Position")
    ax.legend()
    _save(fig, str(Path(figures_dir) / "fig4_permutation_null.png"))


def plot_bootstrap_ci(
    bootstrap_estimates: np.ndarray,
    ci_lower: float,
    ci_upper: float,
    figures_dir: str,
) -> None:
    """fig5: distribution of bootstrap paper_count* estimates + CI bounds."""
    fig, ax = plt.subplots(figsize=(8, 4))
    valid = bootstrap_estimates[~np.isnan(bootstrap_estimates)]
    if len(valid) > 0:
        ax.hist(valid, bins=30, color="darkorange", alpha=0.7, label="bootstrap estimates")
    ax.axvline(ci_lower, color="green", linestyle="--", label=f"CI lower={ci_lower:.1f}")
    ax.axvline(ci_upper, color="green", linestyle=":", label=f"CI upper={ci_upper:.1f}")
    ax.set_xlabel("paper_count*")
    ax.set_ylabel("count")
    ax.set_title("Bootstrap Distribution of paper_count*")
    ax.legend()
    _save(fig, str(Path(figures_dir) / "fig5_bootstrap_ci.png"))


def plot_penalty_sensitivity(
    pen_values: np.ndarray,
    bkps_list: list,
    pen_used: float,
    figures_dir: str,
) -> None:
    """fig6: n_bkps vs penalty (log scale) + BIC penalty marked."""
    fig, ax = plt.subplots(figsize=(8, 4))
    n_bkps_per_pen = [len(bkps) - 1 for bkps in bkps_list]
    ax.semilogx(pen_values, n_bkps_per_pen, "o-", color="teal")
    ax.axvline(pen_used, color="red", linestyle="--", label=f"BIC pen={pen_used:.3f}")
    ax.set_xlabel("penalty (log scale)")
    ax.set_ylabel("n_breakpoints detected")
    ax.set_title("PELT Penalty Sensitivity")
    ax.legend()
    _save(fig, str(Path(figures_dir) / "fig6_penalty_sensitivity.png"))


def save_all_figures(
    paper_counts: np.ndarray,
    cov_values: np.ndarray,
    pelt_results: dict,
    eval_results: dict,
    figures_dir: str,
) -> None:
    """Generate and save all 6 figures."""
    combined = {**pelt_results, **eval_results}

    plot_gate_metrics(combined, figures_dir)
    plot_cov_scatter(
        paper_counts, cov_values,
        pelt_results["paper_count_star"],
        pelt_results["ols_metrics"],
        figures_dir,
    )
    plot_residual_series(
        pelt_results["sorted_paper_counts"],
        pelt_results["residual_cov_sorted"],
        pelt_results["breakpoint_idx"],
        figures_dir,
    )
    plot_permutation_null(
        eval_results.get("null_distribution", np.array([])),
        eval_results.get("observed_bkp_idx"),
        figures_dir,
    )
    plot_bootstrap_ci(
        eval_results.get("bootstrap_estimates", np.array([])),
        eval_results.get("bootstrap_ci_lower", float("nan")),
        eval_results.get("bootstrap_ci_upper", float("nan")),
        figures_dir,
    )
    plot_penalty_sensitivity(
        pelt_results["pen_values"],
        pelt_results["bkps_list"],
        pelt_results["pen_used"],
        figures_dir,
    )
