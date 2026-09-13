import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

FIGURES_DIR = "docs/youra_research/h-e1/figures"


def plot_gate_metrics(he_count: int, mbpp_count: int, output_dir: str = FIGURES_DIR) -> Path:
    labels = ["HE+ Failures", "MBPP+ Failures", "Total"]
    actual = [he_count, mbpp_count, he_count + mbpp_count]
    expected = [34, 100, 134]

    x = np.arange(len(labels))
    width = 0.35
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x - width / 2, actual, width, label="Actual", color="#2196F3")
    ax.bar(x + width / 2, expected, width, label="Expected", color="#4CAF50", alpha=0.7)

    ax.set_ylabel("Count")
    ax.set_title("H-E1 Gate Metrics: Actual vs Expected Failure Counts")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    for i, (a, e) in enumerate(zip(actual, expected)):
        match = "✓" if a == e else "✗"
        ax.annotate(f"{a} {match}", xy=(x[i] - width / 2, a), ha="center", va="bottom")

    out = Path(output_dir) / "gate_metrics.png"
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out


def plot_failure_distribution(he_count: int, mbpp_count: int, output_dir: str = FIGURES_DIR) -> Path:
    total = he_count + mbpp_count
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie([he_count, mbpp_count],
           labels=[f"HE+ ({he_count})", f"MBPP+ ({mbpp_count})"],
           autopct=lambda p: f"{p:.1f}%",
           colors=["#2196F3", "#FF9800"])
    ax.set_title(f"H-E1 Failure Distribution (n={total})")
    out = Path(output_dir) / "failure_distribution.png"
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out


def plot_completeness_matrix(he_failures: dict, mbpp_failures: dict,
                              he_problems: dict, mbpp_problems: dict,
                              output_dir: str = FIGURES_DIR) -> Path:
    all_failures = {**he_failures, **mbpp_failures}
    all_problems = {**he_problems, **mbpp_problems}
    task_ids = sorted(all_failures.keys())

    matrix = np.zeros((len(task_ids), 3), dtype=int)
    for i, tid in enumerate(task_ids):
        rec = all_failures[tid]
        matrix[i, 0] = 1 if rec.get("solution") else 0
        matrix[i, 1] = 1 if rec.get("plus_fail_tests") else 0
        matrix[i, 2] = 1 if tid in all_problems else 0

    fig, ax = plt.subplots(figsize=(6, 16))
    ax.imshow(matrix, aspect="auto", cmap="RdYlGn", vmin=0, vmax=1)
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(["solution_present", "plus_fail_tests_present", "task_in_api"],
                       rotation=20, ha="right")
    ax.set_yticks([])
    ax.set_title(f"Data Completeness Matrix ({len(task_ids)} tasks x 3 checks)\nAll green = PASS")

    out = Path(output_dir) / "completeness_matrix.png"
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out


def plot_failing_tests_histogram(he_failures: dict, mbpp_failures: dict,
                                  output_dir: str = FIGURES_DIR) -> Path:
    all_failures = {**he_failures, **mbpp_failures}
    counts = [len(rec.get("plus_fail_tests", [])) for rec in all_failures.values()]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(counts, bins=20, color="#9C27B0", edgecolor="white")
    ax.set_xlabel("Number of plus_fail_tests")
    ax.set_ylabel("Number of problems")
    ax.set_title(f"Distribution of plus_fail_tests Count (n={len(counts)} problems)")
    ax.axvline(x=1, color="red", linestyle="--", label="threshold=1")
    ax.legend()

    out = Path(output_dir) / "failing_tests_histogram.png"
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out


def generate_all(he_failures: dict, mbpp_failures: dict,
                 he_problems: dict, mbpp_problems: dict,
                 output_dir: str = FIGURES_DIR) -> None:
    plot_gate_metrics(len(he_failures), len(mbpp_failures), output_dir)
    plot_failure_distribution(len(he_failures), len(mbpp_failures), output_dir)
    plot_completeness_matrix(he_failures, mbpp_failures, he_problems, mbpp_problems, output_dir)
    plot_failing_tests_histogram(he_failures, mbpp_failures, output_dir)
