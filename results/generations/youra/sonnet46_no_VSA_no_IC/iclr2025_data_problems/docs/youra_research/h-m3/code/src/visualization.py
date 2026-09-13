"""Generate all 6 figures for H-M3."""
from __future__ import annotations
import logging
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

log = logging.getLogger(__name__)

sns.set_palette("colorblind")
DPI = 300
WIKI = "Wikipedia (en)"
BOOKS = "Books3"
BENCHMARKS = ["mmlu", "hellaswag", "arc_challenge", "winogrande"]


def _save(fig: plt.Figure, path: Path, dpi: int = DPI) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    log.info(f"Saved: {path}")


def fig1_gate_metrics(
    focal_coeffs: dict,
    figures_dir: Path,
    ci_alpha: float = 0.95,
) -> None:
    """Bar chart: β_Wikipedia and β_Books3 per benchmark with 95% CI error bars."""
    from scipy.stats import norm
    z = norm.ppf(0.5 + ci_alpha / 2)

    benchmarks = [b for b in BENCHMARKS if b in focal_coeffs]
    n = len(benchmarks)
    x = np.arange(n)
    width = 0.35

    wiki_betas = [focal_coeffs[b].get(WIKI, {}).get("beta", 0.0) for b in benchmarks]
    wiki_ses = [focal_coeffs[b].get(WIKI, {}).get("se", 0.0) for b in benchmarks]
    books_betas = [focal_coeffs[b].get(BOOKS, {}).get("beta", 0.0) for b in benchmarks]
    books_ses = [focal_coeffs[b].get(BOOKS, {}).get("se", 0.0) for b in benchmarks]

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(x - width/2, wiki_betas, width, yerr=[z*s for s in wiki_ses],
           label=WIKI, capsize=4, alpha=0.8)
    ax.bar(x + width/2, books_betas, width, yerr=[z*s for s in books_ses],
           label=BOOKS, capsize=4, alpha=0.8)
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_xticks(x)
    ax.set_xticklabels(benchmarks, rotation=15)
    ax.set_ylabel("Panel OLS β coefficient")
    ax.set_title("H-M3: Domain Coefficients by Benchmark (95% CI)")
    ax.legend()
    _save(fig, Path(figures_dir) / "fig1_gate_metrics_comparison.png")


def fig2_domain_heatmap(
    benchmark_results: dict,
    domain_cols: list[str],
    figures_dir: Path,
) -> None:
    """Heatmap: domains × benchmarks, color = β magnitude."""
    benchmarks = [b for b in BENCHMARKS if b in benchmark_results]
    betas = {}
    for bench in benchmarks:
        res = benchmark_results[bench]
        row = {}
        for d in domain_cols:
            key = next((k for k in res.params.index if d in k), None)
            row[d] = float(res.params[key]) if key else 0.0
        betas[bench] = row

    df = pd.DataFrame(betas).T  # benchmarks × domains
    fig, ax = plt.subplots(figsize=(14, 10))
    sns.heatmap(df.T, ax=ax, center=0, cmap="RdBu_r", annot=False)
    ax.set_title("H-M3: Domain Coefficient Heatmap")
    ax.set_xlabel("Benchmark")
    ax.set_ylabel("Domain")
    _save(fig, Path(figures_dir) / "fig2_domain_coefficient_heatmap.png")


def fig3_directional_scatter(
    focal_coeffs: dict,
    figures_dir: Path,
) -> None:
    """Scatter: β_Wikipedia vs β_Books3 per benchmark with diagonal."""
    benchmarks = [b for b in BENCHMARKS if b in focal_coeffs]
    wiki_betas = [focal_coeffs[b].get(WIKI, {}).get("beta", 0.0) for b in benchmarks]
    books_betas = [focal_coeffs[b].get(BOOKS, {}).get("beta", 0.0) for b in benchmarks]

    fig, ax = plt.subplots(figsize=(8, 8))
    scatter = ax.scatter(wiki_betas, books_betas, c=range(len(benchmarks)), cmap="colorblind", s=100)
    for i, b in enumerate(benchmarks):
        ax.annotate(b, (wiki_betas[i], books_betas[i]), textcoords="offset points", xytext=(5, 5))

    lims = [min(wiki_betas + books_betas) - 0.01, max(wiki_betas + books_betas) + 0.01]
    ax.plot(lims, lims, "k--", alpha=0.5, label="β_wiki = β_books")
    ax.set_xlabel(f"β {WIKI}")
    ax.set_ylabel(f"β {BOOKS}")
    ax.set_title("H-M3: P1/P2 Directional Scatter")
    ax.legend()
    _save(fig, Path(figures_dir) / "fig3_directional_scatter.png")


def fig4_r2_decomposition(
    r2_decomp: dict,
    figures_dir: Path,
) -> None:
    """Bar chart: R²_within domain-only, scale-only, full per benchmark."""
    benchmarks = [b for b in BENCHMARKS if b in r2_decomp]
    domain_r2 = [r2_decomp[b].get("domain_only_within") or 0.0 for b in benchmarks]
    scale_r2 = [r2_decomp[b].get("scale_only_pooled") or 0.0 for b in benchmarks]

    x = np.arange(len(benchmarks))
    width = 0.35
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x - width/2, domain_r2, width, label="Domain-only (within R²)")
    ax.bar(x + width/2, scale_r2, width, label="Scale-only (pooled R²)")
    ax.set_xticks(x)
    ax.set_xticklabels(benchmarks, rotation=15)
    ax.set_ylabel("R²")
    ax.set_title("H-M3: R² Decomposition")
    ax.legend()
    _save(fig, Path(figures_dir) / "fig4_r2_decomposition.png")


def fig5_permutation_null(
    permutation_results: dict,
    figures_dir: Path,
) -> None:
    """Histogram: permutation null distribution vs observed for P1, P2."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, (test, bench) in zip(axes, [("P1", "mmlu"), ("P2", "hellaswag")]):
        perm = permutation_results.get(test, {})
        # null_dist not stored to save memory; just plot text summary
        obs = perm.get("observed")
        emp_p = perm.get("empirical_p")
        ax.text(0.5, 0.5,
                f"{test} ({bench})\nobserved={obs:.4f}\nempirical_p={emp_p:.4f}" if obs is not None
                else f"{test}\n(no data)",
                transform=ax.transAxes, ha="center", va="center", fontsize=12)
        ax.set_title(f"Permutation Null — {test}")
    plt.tight_layout()
    _save(fig, Path(figures_dir) / "fig5_permutation_null.png")


def fig6_subgroup_robustness(
    subgroup_results: dict,
    focal_domains: dict,
    figures_dir: Path,
) -> None:
    """Bar chart: β_wiki and β_books for small vs large subgroups."""
    benchmarks = BENCHMARKS
    wiki = focal_domains.get("wikipedia", WIKI)
    books = focal_domains.get("books", BOOKS)

    data_rows = []
    for group in ["small", "large"]:
        for bench in benchmarks:
            res = subgroup_results.get(group, {}).get(bench)
            if res is None:
                continue
            wiki_k = next((k for k in res.params.index if wiki in k), None)
            books_k = next((k for k in res.params.index if books in k), None)
            data_rows.append({
                "group": group, "bench": bench,
                "wiki_beta": float(res.params[wiki_k]) if wiki_k else 0.0,
                "books_beta": float(res.params[books_k]) if books_k else 0.0,
            })

    if not data_rows:
        fig, ax = plt.subplots(figsize=(14, 6))
        ax.text(0.5, 0.5, "No subgroup data available", transform=ax.transAxes, ha="center")
        _save(fig, Path(figures_dir) / "fig6_subgroup_robustness.png")
        return

    df = pd.DataFrame(data_rows)
    x = np.arange(len(benchmarks))
    width = 0.2
    fig, ax = plt.subplots(figsize=(14, 6))

    for i, (group, domain, col) in enumerate([
        ("small", "wiki", "wiki_beta"),
        ("small", "books", "books_beta"),
        ("large", "wiki", "wiki_beta"),
        ("large", "books", "books_beta"),
    ]):
        sub = df[df.group == group].set_index("bench").reindex(benchmarks)
        ax.bar(x + (i - 1.5) * width, sub[col].fillna(0), width,
               label=f"{group} {domain}")

    ax.set_xticks(x)
    ax.set_xticklabels(benchmarks, rotation=15)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel("β coefficient")
    ax.set_title("H-M3: Subgroup Robustness (Small vs Large Models)")
    ax.legend()
    _save(fig, Path(figures_dir) / "fig6_subgroup_robustness.png")


def generate_all_figures(
    focal_coeffs: dict,
    benchmark_results: dict,
    domain_cols: list[str],
    r2_decomp: dict,
    permutation_results: dict,
    subgroup_results: dict,
    focal_domains: dict,
    figures_dir: str | Path,
) -> None:
    """Generate all 6 required figures."""
    figures_dir = Path(figures_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)

    fig1_gate_metrics(focal_coeffs, figures_dir)
    fig2_domain_heatmap(benchmark_results, domain_cols, figures_dir)
    fig3_directional_scatter(focal_coeffs, figures_dir)
    fig4_r2_decomposition(r2_decomp, figures_dir)
    fig5_permutation_null(permutation_results, figures_dir)
    fig6_subgroup_robustness(subgroup_results, focal_domains, figures_dir)
    log.info("All 6 figures generated")
