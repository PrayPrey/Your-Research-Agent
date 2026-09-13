import json
import os
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import config

def compute_metrics(results: list[dict]) -> dict:
    n = len(results)
    warning_rate = sum(1 for r in results if r["actionable_count"] >= 1) / n
    avg_warnings = sum(r["actionable_count"] for r in results) / n

    warning_type_distribution = Counter(
        m["type"] for r in results for m in r["messages"]
    )

    top_10_warning_codes = Counter(
        code for r in results for code in r["warning_codes"]
    ).most_common(10)

    gate_passed = warning_rate >= config.GATE_THRESHOLD

    return {
        "warning_rate": warning_rate,
        "avg_warnings": avg_warnings,
        "warning_type_distribution": dict(warning_type_distribution),
        "top_10_warning_codes": top_10_warning_codes,
        "gate_passed": gate_passed,
    }

def plot_gate_metrics(metrics: dict) -> None:
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(["Target", "Actual"], [config.GATE_THRESHOLD, metrics["warning_rate"]], color=["gray", "blue"])
    ax.set_ylabel("Warning Rate")
    ax.set_title("Gate Metrics: Target vs Actual")
    ax.axhline(y=config.GATE_THRESHOLD, color="red", linestyle="--", label="Threshold")
    ax.legend()
    os.makedirs(config.FIGURES_DIR, exist_ok=True)
    fig.savefig(os.path.join(config.FIGURES_DIR, "gate_metrics.png"), dpi=100)
    plt.close(fig)

def plot_warning_distribution(results: list[dict]) -> None:
    counts = [r["actionable_count"] for r in results]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(counts, bins=range(0, max(counts) + 2), edgecolor="black", align="left")
    ax.set_xlabel("Actionable Warnings per Problem")
    ax.set_ylabel("Count")
    ax.set_title("Distribution of Warnings per Problem")
    os.makedirs(config.FIGURES_DIR, exist_ok=True)
    fig.savefig(os.path.join(config.FIGURES_DIR, "warning_distribution.png"), dpi=100)
    plt.close(fig)

def plot_warning_type_breakdown(metrics: dict) -> None:
    dist = metrics["warning_type_distribution"]
    if not dist:
        return
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(dist.values(), labels=dist.keys(), autopct="%1.1f%%")
    ax.set_title("Warning Type Breakdown")
    os.makedirs(config.FIGURES_DIR, exist_ok=True)
    fig.savefig(os.path.join(config.FIGURES_DIR, "warning_type_breakdown.png"), dpi=100)
    plt.close(fig)

def plot_top_warning_codes(metrics: dict) -> None:
    codes = metrics["top_10_warning_codes"]
    if not codes:
        return
    labels, counts = zip(*codes)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(labels, counts)
    ax.set_xlabel("Count")
    ax.set_title("Top 10 Warning Codes")
    ax.invert_yaxis()
    os.makedirs(config.FIGURES_DIR, exist_ok=True)
    fig.savefig(os.path.join(config.FIGURES_DIR, "top_warning_codes.png"), dpi=100)
    plt.close(fig)

def evaluate(results: list[dict]) -> dict:
    metrics = compute_metrics(results)
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    with open(config.METRICS_FILE, "w") as f:
        json.dump(metrics, f, indent=2)

    plot_gate_metrics(metrics)
    plot_warning_distribution(results)
    plot_warning_type_breakdown(metrics)
    plot_top_warning_codes(metrics)

    return metrics
