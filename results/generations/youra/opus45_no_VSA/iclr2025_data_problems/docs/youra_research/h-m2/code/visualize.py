import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


def plot_gate_metrics(target: dict, actual: dict, out_dir: str) -> None:
    """Bar chart comparing target vs actual gate metrics."""
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    metrics = list(target.keys())
    x = np.arange(len(metrics))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 5))
    bars1 = ax.bar(x - width / 2, [target[m] for m in metrics], width, label="Target", color="#4CAF50")
    bars2 = ax.bar(x + width / 2, [actual[m] for m in metrics], width, label="Actual", color="#2196F3")

    ax.set_ylabel("Value")
    ax.set_title("H-M2 Gate Metrics: Target vs Actual")
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.legend()
    ax.axhline(y=1.5, color="red", linestyle="--", label="Gate threshold (1.5)")

    plt.tight_layout()
    plt.savefig(f"{out_dir}/gate_metrics.png", dpi=150)
    plt.close()


def plot_accuracy_by_fraction(results: dict, out_dir: str) -> None:
    """Accuracy drop curves by removal fraction."""
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    fractions = sorted(results.keys())
    baseline_accs = [results[f]["baseline"] for f in fractions]
    high_ccr_accs = [results[f]["high_ccr"] for f in fractions]
    random_accs = [results[f]["random"] for f in fractions]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(fractions, baseline_accs, "o-", label="Baseline", color="#4CAF50")
    ax.plot(fractions, high_ccr_accs, "s-", label="High-CCR Removal", color="#F44336")
    ax.plot(fractions, random_accs, "^-", label="Random Removal", color="#2196F3")

    ax.set_xlabel("Removal Fraction")
    ax.set_ylabel("MMLU Accuracy")
    ax.set_title("H-M2: Accuracy by Removal Condition")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(f"{out_dir}/accuracy_by_fraction.png", dpi=150)
    plt.close()


def plot_bootstrap_distribution(ratios: np.ndarray, ci: tuple, out_dir: str) -> None:
    """Histogram of bootstrap degradation ratios with CI."""
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(ratios, bins=50, color="#2196F3", alpha=0.7, edgecolor="black")
    ax.axvline(x=ci[0], color="red", linestyle="--", label=f"95% CI: [{ci[0]:.2f}, {ci[1]:.2f}]")
    ax.axvline(x=ci[1], color="red", linestyle="--")
    ax.axvline(x=1.0, color="green", linestyle="-", linewidth=2, label="Null (ratio=1.0)")
    ax.axvline(x=1.5, color="orange", linestyle="-", linewidth=2, label="Gate (ratio=1.5)")

    ax.set_xlabel("Degradation Ratio")
    ax.set_ylabel("Frequency")
    ax.set_title("H-M2: Bootstrap Distribution of Degradation Ratio")
    ax.legend()

    plt.tight_layout()
    plt.savefig(f"{out_dir}/bootstrap_distribution.png", dpi=150)
    plt.close()
