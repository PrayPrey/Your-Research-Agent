from math import isfinite
from pathlib import Path

import matplotlib.pyplot as plt


def plot_success_rate(summary: dict, out_path: str) -> None:
    """Bar chart of success rate."""
    fig, ax = plt.subplots(figsize=(6, 4))
    rate = summary["completion_rate"] * 100
    ax.bar(["Completion Rate"], [rate], color="steelblue")
    ax.axhline(y=95, color="red", linestyle="--", label="Threshold (95%)")
    ax.set_ylabel("Percentage")
    ax.set_ylim(0, 105)
    ax.set_title("Model Extraction Success Rate")
    ax.legend()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_cv_pr_distribution(results: list[dict], out_path: str) -> None:
    """Histogram of CV_PR values."""
    vals = [r["model_cv_pr"] for r in results if isfinite(r["model_cv_pr"])]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(vals, bins=30, color="steelblue", edgecolor="white")
    ax.axvline(x=sum(vals) / len(vals), color="red", linestyle="--", label=f"Mean: {sum(vals)/len(vals):.3f}")
    ax.set_xlabel("CV_PR")
    ax.set_ylabel("Count")
    ax.set_title("Distribution of CV_PR Across Models")
    ax.legend()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
