"""Evaluation, persistence, and visualization for H-E1."""

import json
import re
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import yaml
from statsmodels.stats.proportion import proportion_confint

from config import ExperimentConfig
from executor import ErrorCategory


def calculate_prevalence(results: list[dict], config: ExperimentConfig) -> dict:
    """Calculate runtime error prevalence with Wilson confidence interval.

    Args:
        results: List of execution result dicts with 'category' key
        config: Experiment configuration

    Returns:
        Dict with prevalence metrics
    """
    categories = [r["category"] for r in results]

    n_total = len(categories)
    n_pass = sum(1 for c in categories if c == ErrorCategory.PASS.value)
    n_failures = n_total - n_pass
    n_runtime = sum(1 for c in categories if c == ErrorCategory.RUNTIME_ERROR.value)
    n_syntax = sum(1 for c in categories if c == ErrorCategory.SYNTAX_ERROR.value)
    n_wrong = sum(1 for c in categories if c == ErrorCategory.WRONG_OUTPUT.value)
    n_timeout = sum(1 for c in categories if c == ErrorCategory.TIMEOUT.value)

    if n_failures == 0:
        prevalence = 0.0
        ci_lower, ci_upper = 0.0, 0.0
    else:
        prevalence = n_runtime / n_failures
        alpha = 1 - config.ci_confidence
        ci_lower, ci_upper = proportion_confint(
            n_runtime, n_failures, alpha=alpha, method=config.ci_method
        )

    return {
        "prevalence": prevalence,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "n_runtime": n_runtime,
        "n_failures": n_failures,
        "n_total": n_total,
        "n_pass": n_pass,
        "n_syntax": n_syntax,
        "n_wrong": n_wrong,
        "n_timeout": n_timeout,
        "pass_rate": n_pass / n_total if n_total > 0 else 0.0,
    }


def check_gate(metrics: dict, threshold: float = 0.30) -> bool:
    """Check if gate condition is satisfied.

    Gate condition: CI lower bound >= threshold

    Args:
        metrics: Dict with 'ci_lower' key
        threshold: Gate threshold (default 0.30)

    Returns:
        True if gate passes
    """
    return metrics["ci_lower"] >= threshold


def save_results(results: list[dict], metrics: dict, config: ExperimentConfig) -> None:
    """Save execution results and metrics to files.

    Args:
        results: List of per-problem execution results
        metrics: Aggregate metrics dict
        config: Experiment configuration
    """
    # Ensure directories exist
    Path(config.results_dir).mkdir(parents=True, exist_ok=True)
    Path(config.figures_dir).mkdir(parents=True, exist_ok=True)

    # Save execution results as JSON
    with open(config.output_json, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved execution results to {config.output_json}")

    # Save metrics as YAML
    with open(config.output_metrics, "w") as f:
        yaml.dump(metrics, f, default_flow_style=False)
    print(f"Saved metrics to {config.output_metrics}")


def plot_error_distribution(results: list[dict], figures_dir: str) -> None:
    """Generate pie chart of error category distribution.

    Args:
        results: List of execution result dicts
        figures_dir: Directory to save figure
    """
    categories = [r["category"] for r in results]
    counts = Counter(categories)

    labels = []
    sizes = []
    colors = ["#2ecc71", "#e74c3c", "#3498db", "#f39c12", "#9b59b6"]

    order = [
        ErrorCategory.PASS.value,
        ErrorCategory.RUNTIME_ERROR.value,
        ErrorCategory.WRONG_OUTPUT.value,
        ErrorCategory.SYNTAX_ERROR.value,
        ErrorCategory.TIMEOUT.value,
    ]

    for cat in order:
        if counts.get(cat, 0) > 0:
            labels.append(f"{cat} ({counts[cat]})")
            sizes.append(counts[cat])

    plt.figure(figsize=(8, 8))
    plt.pie(sizes, labels=labels, colors=colors[:len(sizes)], autopct='%1.1f%%',
            startangle=90, textprops={'fontsize': 11})
    plt.title("Error Distribution (MBPP Test Set)", fontsize=14)
    plt.tight_layout()
    plt.savefig(f"{figures_dir}/error_distribution.png", dpi=150)
    plt.close()
    print(f"Saved error_distribution.png")


def plot_runtime_error_types(results: list[dict], figures_dir: str) -> None:
    """Generate bar chart of runtime error types.

    Args:
        results: List of execution result dicts
        figures_dir: Directory to save figure
    """
    error_types = []

    for r in results:
        if r["category"] == ErrorCategory.RUNTIME_ERROR.value and r.get("stderr"):
            stderr = r["stderr"]
            # Extract error type from last line (e.g., "TypeError: ...")
            lines = stderr.strip().split("\n")
            if lines:
                last_line = lines[-1]
                # Match error type at start of line
                match = re.match(r"^(\w+Error|\w+Exception)", last_line)
                if match:
                    error_types.append(match.group(1))
                else:
                    error_types.append("Other")

    if not error_types:
        print("No runtime errors to plot")
        return

    counts = Counter(error_types)
    # Sort by count descending
    sorted_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    labels, values = zip(*sorted_items) if sorted_items else ([], [])

    plt.figure(figsize=(10, 6))
    bars = plt.bar(range(len(labels)), values, color="#e74c3c")
    plt.xticks(range(len(labels)), labels, rotation=45, ha="right")
    plt.xlabel("Error Type", fontsize=12)
    plt.ylabel("Count", fontsize=12)
    plt.title("Runtime Error Type Distribution", fontsize=14)

    # Add count labels on bars
    for bar, val in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                 str(val), ha="center", va="bottom", fontsize=10)

    plt.tight_layout()
    plt.savefig(f"{figures_dir}/runtime_error_types.png", dpi=150)
    plt.close()
    print(f"Saved runtime_error_types.png")


def plot_prevalence_ci(metrics: dict, figures_dir: str) -> None:
    """Generate point estimate with 95% Wilson CI error bars.

    Args:
        metrics: Metrics dict with prevalence and CI bounds
        figures_dir: Directory to save figure
    """
    prevalence = metrics["prevalence"]
    ci_lower = metrics["ci_lower"]
    ci_upper = metrics["ci_upper"]

    plt.figure(figsize=(8, 6))

    # Point estimate with error bars
    plt.errorbar(
        x=[1], y=[prevalence * 100],
        yerr=[[prevalence * 100 - ci_lower * 100], [ci_upper * 100 - prevalence * 100]],
        fmt="o", markersize=12, color="#3498db", capsize=10, capthick=2, elinewidth=2
    )

    # Gate threshold line
    plt.axhline(y=30, color="#e74c3c", linestyle="--", linewidth=2, label="Gate threshold (30%)")

    plt.xlim(0.5, 1.5)
    plt.ylim(0, 100)
    plt.xticks([1], ["Runtime Error\nPrevalence"])
    plt.ylabel("Prevalence (%)", fontsize=12)
    plt.title(f"Runtime Error Prevalence with 95% Wilson CI\n({prevalence*100:.1f}% [{ci_lower*100:.1f}%, {ci_upper*100:.1f}%])", fontsize=14)
    plt.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(f"{figures_dir}/prevalence_ci.png", dpi=150)
    plt.close()
    print(f"Saved prevalence_ci.png")


def plot_gate_comparison(metrics: dict, figures_dir: str, threshold: float = 0.30) -> None:
    """Generate bar chart comparing target vs actual prevalence.

    Args:
        metrics: Metrics dict with prevalence and CI bounds
        figures_dir: Directory to save figure
        threshold: Gate threshold
    """
    prevalence = metrics["prevalence"]
    ci_lower = metrics["ci_lower"]
    gate_passed = ci_lower >= threshold

    plt.figure(figsize=(8, 6))

    x = [0, 1]
    heights = [threshold * 100, prevalence * 100]
    colors = ["#95a5a6", "#2ecc71" if gate_passed else "#e74c3c"]
    labels = ["Target\n(30%)", f"Actual\n({prevalence*100:.1f}%)"]

    bars = plt.bar(x, heights, color=colors, width=0.5)

    # Add CI error bar on actual
    plt.errorbar(
        x=[1], y=[prevalence * 100],
        yerr=[[prevalence * 100 - ci_lower * 100], [metrics["ci_upper"] * 100 - prevalence * 100]],
        fmt="none", color="black", capsize=8, capthick=2, elinewidth=2
    )

    # Gate result annotation
    result_text = "GATE PASSED" if gate_passed else "GATE FAILED"
    result_color = "#2ecc71" if gate_passed else "#e74c3c"
    plt.text(0.5, max(heights) + 10, result_text, ha="center", fontsize=16,
             fontweight="bold", color=result_color)

    plt.xticks(x, labels, fontsize=12)
    plt.ylabel("Prevalence (%)", fontsize=12)
    plt.ylim(0, max(heights) + 20)
    plt.title("Gate Comparison: Runtime Error Prevalence", fontsize=14)
    plt.tight_layout()
    plt.savefig(f"{figures_dir}/gate_comparison.png", dpi=150)
    plt.close()
    print(f"Saved gate_comparison.png")


def generate_all_figures(results: list[dict], metrics: dict, config: ExperimentConfig) -> None:
    """Generate all visualization figures.

    Args:
        results: List of execution result dicts
        metrics: Aggregate metrics dict
        config: Experiment configuration
    """
    Path(config.figures_dir).mkdir(parents=True, exist_ok=True)

    plot_error_distribution(results, config.figures_dir)
    plot_runtime_error_types(results, config.figures_dir)
    plot_prevalence_ci(metrics, config.figures_dir)
    plot_gate_comparison(metrics, config.figures_dir, config.gate_threshold)

    print(f"\nAll figures saved to {config.figures_dir}/")
