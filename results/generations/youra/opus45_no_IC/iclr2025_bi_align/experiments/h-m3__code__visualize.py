import os
import numpy as np
import matplotlib.pyplot as plt


def plot_tercile_bar_chart(tercile_rates: dict, tercile_counts: dict, out_path: str) -> None:
    fig, ax = plt.subplots(figsize=(8, 6))
    labels = ["T1 (Low Δ)", "T2 (Mid Δ)", "T3 (High Δ)"]
    rates = [tercile_rates[1], tercile_rates[2], tercile_rates[3]]
    counts = [tercile_counts[1], tercile_counts[2], tercile_counts[3]]

    bars = ax.bar(labels, rates, color=["#2ecc71", "#f1c40f", "#e74c3c"], edgecolor="black")

    for bar, rate, count in zip(bars, rates, counts):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                f"{rate:.3f}\n(n={count:,})", ha="center", va="bottom", fontsize=10)

    ax.set_ylabel("Continuation Rate", fontsize=12)
    ax.set_xlabel("Formality Delta Tercile", fontsize=12)
    ax.set_title("H-M3: Continuation Rate by Formality Delta Tercile", fontsize=14)
    ax.set_ylim(0, max(rates) * 1.2)
    ax.axhline(y=np.mean(rates), color="gray", linestyle="--", label=f"Mean: {np.mean(rates):.3f}")
    ax.legend()

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_delta_histogram(deltas: np.ndarray, t1: float, t2: float, out_path: str) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(deltas, bins=50, color="#3498db", edgecolor="black", alpha=0.7)

    ax.axvline(x=t1, color="green", linestyle="--", linewidth=2, label=f"T1 boundary: {t1:.3f}")
    ax.axvline(x=t2, color="red", linestyle="--", linewidth=2, label=f"T2 boundary: {t2:.3f}")

    ax.set_xlabel("Formality Delta (|human - AI|)", fontsize=12)
    ax.set_ylabel("Count", fontsize=12)
    ax.set_title("Distribution of Formality Deltas with Tercile Boundaries", fontsize=14)
    ax.legend()

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_delta_vs_continuation_scatter(
    deltas: np.ndarray,
    continuations: np.ndarray,
    out_path: str,
    sample_size: int = 5000
) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))

    if len(deltas) > sample_size:
        idx = np.random.choice(len(deltas), sample_size, replace=False)
        deltas_sample = deltas[idx]
        cont_sample = continuations[idx]
    else:
        deltas_sample = deltas
        cont_sample = continuations

    jitter = np.random.normal(0, 0.05, len(cont_sample))
    ax.scatter(deltas_sample, cont_sample + jitter, alpha=0.3, s=10, c="#9b59b6")

    z = np.polyfit(deltas_sample, cont_sample, 1)
    p = np.poly1d(z)
    x_line = np.linspace(deltas_sample.min(), deltas_sample.max(), 100)
    ax.plot(x_line, p(x_line), "r-", linewidth=2, label=f"Trend: slope={z[0]:.4f}")

    ax.set_xlabel("Formality Delta", fontsize=12)
    ax.set_ylabel("Continuation (jittered)", fontsize=12)
    ax.set_title("Delta vs Continuation (Sampled)", fontsize=14)
    ax.legend()

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_bootstrap_distribution(
    boot_rhos: np.ndarray,
    observed_rho: float,
    out_path: str
) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(boot_rhos, bins=50, color="#1abc9c", edgecolor="black", alpha=0.7)

    ax.axvline(x=observed_rho, color="red", linestyle="-", linewidth=2,
               label=f"Observed ρ: {observed_rho:.4f}")
    ax.axvline(x=0, color="black", linestyle="--", linewidth=1.5, label="Null (ρ=0)")

    ci_low = np.percentile(boot_rhos, 2.5)
    ci_high = np.percentile(boot_rhos, 97.5)
    ax.axvline(x=ci_low, color="blue", linestyle=":", linewidth=1.5)
    ax.axvline(x=ci_high, color="blue", linestyle=":", linewidth=1.5,
               label=f"95% CI: [{ci_low:.4f}, {ci_high:.4f}]")

    ax.set_xlabel("Bootstrap Spearman ρ", fontsize=12)
    ax.set_ylabel("Count", fontsize=12)
    ax.set_title("Bootstrap Distribution of Spearman Correlation", fontsize=14)
    ax.legend()

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()
