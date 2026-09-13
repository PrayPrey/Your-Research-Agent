"""Visualization for H-C1 doctest prevalence scan."""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def plot_gate_metrics(aggregate: dict, out_dir: str) -> None:
    """Bar chart of pattern_rate, ast_rate, executable_rate with 3% threshold line."""
    labels = ["Pattern Rate\n(Phase A)", "AST Rate\n(Phase B)", "Executable Rate\n(Phase C)"]
    values = [
        aggregate["doctest_pattern_rate"],
        aggregate["doctest_ast_rate"],
        aggregate["doctest_executable_rate"],
    ]
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, values, color=["#4C72B0", "#55A868", "#C44E52"])
    ax.axhline(y=0.03, color="red", linestyle="--", linewidth=1.5, label="3% threshold (PASS)")
    ax.axhline(y=0.01, color="orange", linestyle="--", linewidth=1.0, label="1% threshold (SCOPE)")
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.001,
                f"{val:.3f}", ha="center", va="bottom", fontsize=10)
    ax.set_ylabel("Rate (fraction of 10,000 files)")
    ax.set_title("H-C1: Doctest Prevalence by Phase")
    ax.legend()
    ax.set_ylim(0, max(max(values) * 1.2, 0.05))
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "gate_metrics_comparison.png"), dpi=150)
    plt.close()


def plot_prevalence_breakdown(aggregate: dict, out_dir: str) -> None:
    """Stacked bar of no-doctest / pattern-only / ast-only / executable fractions."""
    n = aggregate["n_sampled"]
    n_exec = aggregate["n_executable_positive"]
    n_ast = aggregate["n_ast_positive"]
    n_pat = aggregate["n_pattern_positive"]

    executable = n_exec / n
    ast_only = (n_ast - n_exec) / n
    pattern_only = (n_pat - n_ast) / n
    none_frac = (n - n_pat) / n

    fig, ax = plt.subplots(figsize=(6, 5))
    bottom = 0
    colors = ["#d9d9d9", "#fdae61", "#abd9e9", "#2c7bb6"]
    labels = ["No doctest", "Pattern only", "AST only", "Executable"]
    for val, color, label in zip([none_frac, pattern_only, ast_only, executable], colors, labels):
        ax.bar(["Files"], [val], bottom=bottom, color=color, label=label)
        if val > 0.005:
            ax.text(0, bottom + val / 2, f"{val:.3f}", ha="center", va="center", fontsize=9)
        bottom += val
    ax.set_ylabel("Fraction of sampled files")
    ax.set_title("H-C1: Doctest Prevalence Breakdown")
    ax.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "prevalence_breakdown.png"), dpi=150)
    plt.close()


def plot_token_pool(aggregate: dict, out_dir: str) -> None:
    """Horizontal bar of estimated_token_pool_M vs 500M target."""
    pool = aggregate["estimated_token_pool_M"]
    target = 500.0
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.barh(["Estimated pool", "Target (500M)"], [pool, target],
            color=["#2c7bb6" if pool >= target else "#d7191c", "#d9d9d9"])
    ax.set_xlabel("Tokens (millions)")
    ax.set_title("H-C1: Estimated Token Pool from Executable Doctests")
    ax.axvline(x=500, color="red", linestyle="--", linewidth=1.5, label="500M target")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "token_pool_estimate.png"), dpi=150)
    plt.close()


def plot_error_distribution(per_file: list, out_dir: str) -> None:
    """Pie chart of error_type distribution for Phase C failures."""
    from collections import Counter
    failed = [r["error_type"] for r in per_file if r.get("phase_c") is False and r.get("error_type")]
    if not failed:
        return
    counts = Counter(failed)
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(counts.values(), labels=counts.keys(), autopct="%1.1f%%", startangle=90)
    ax.set_title("H-C1: Phase C Failure Types")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "error_type_distribution.png"), dpi=150)
    plt.close()


def plot_file_size_distribution(per_file: list, out_dir: str) -> None:
    """Overlapping histograms of token counts for executable vs non-executable files."""
    exec_tokens = [r["estimated_tokens"] for r in per_file if r.get("phase_c") is True and r["estimated_tokens"] > 0]
    non_exec_tokens = [r["estimated_tokens"] for r in per_file if r.get("phase_c") is False and r["estimated_tokens"] > 0]
    # Fallback: use content_len for files where estimated_tokens == 0
    if not exec_tokens and not non_exec_tokens:
        return
    fig, ax = plt.subplots(figsize=(8, 5))
    bins = np.linspace(0, max((max(exec_tokens) if exec_tokens else 0,
                               max(non_exec_tokens) if non_exec_tokens else 0, 100)), 50)
    if exec_tokens:
        ax.hist(exec_tokens, bins=bins, alpha=0.6, label="Executable", color="#2c7bb6")
    if non_exec_tokens:
        ax.hist(non_exec_tokens, bins=bins, alpha=0.6, label="Non-executable", color="#d7191c")
    ax.set_xlabel("Estimated tokens")
    ax.set_ylabel("Count")
    ax.set_title("H-C1: File Size Distribution (Executable vs Non-executable)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "file_size_distribution.png"), dpi=150)
    plt.close()


def generate_all(aggregate: dict, per_file: list, out_dir: str) -> None:
    """Generate all 5 figures."""
    os.makedirs(out_dir, exist_ok=True)
    plot_gate_metrics(aggregate, out_dir)
    plot_prevalence_breakdown(aggregate, out_dir)
    plot_token_pool(aggregate, out_dir)
    plot_error_distribution(per_file, out_dir)
    plot_file_size_distribution(per_file, out_dir)
    print(f"All figures saved to {out_dir}/")
