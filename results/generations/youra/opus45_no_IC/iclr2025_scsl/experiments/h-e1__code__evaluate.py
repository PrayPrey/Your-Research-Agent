"""Evaluation metrics and visualization."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import precision_score, recall_score
from scipy.stats import mannwhitneyu


def compute_gate_metrics(pred_minority: np.ndarray, minority_mask: np.ndarray) -> dict:
    """Compute precision and recall for minority detection."""
    precision = precision_score(minority_mask, pred_minority, zero_division=0)
    recall = recall_score(minority_mask, pred_minority, zero_division=0)
    return {"precision": precision, "recall": recall}


def mann_whitney_test(d_i: np.ndarray, minority_mask: np.ndarray) -> tuple:
    """Mann-Whitney U test: minority d_i > majority d_i."""
    d_i_valid = d_i.copy()
    d_i_valid[d_i_valid == -1] = 999

    minority_d = d_i_valid[minority_mask]
    majority_d = d_i_valid[~minority_mask]

    stat, pvalue = mannwhitneyu(minority_d, majority_d, alternative='greater')
    return float(stat), float(pvalue)


def plot_gate_metrics_bar(results: dict, out_path: str) -> None:
    """Bar chart of precision/recall vs thresholds."""
    fig, ax = plt.subplots(figsize=(8, 5))
    metrics = ["precision", "recall"]
    values = [results["precision"], results["recall"]]
    thresholds = [0.5, 0.3]
    colors = ["#4CAF50" if v > t else "#F44336" for v, t in zip(values, thresholds)]

    bars = ax.bar(metrics, values, color=colors, edgecolor="black")
    ax.axhline(y=0.5, color="gray", linestyle="--", label="Precision threshold")
    ax.axhline(y=0.3, color="gray", linestyle=":", label="Recall threshold")

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f"{val:.3f}", ha="center", va="bottom", fontsize=12)

    ax.set_ylabel("Score")
    ax.set_title("Gate Metrics: Minority Detection")
    ax.set_ylim(0, 1)
    ax.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_onset_delay_histogram(d_i: np.ndarray, minority_mask: np.ndarray, out_path: str) -> None:
    """Histogram of onset delays by group."""
    d_i_plot = d_i.copy().astype(float)
    d_i_plot[d_i_plot == -1] = np.nan

    fig, ax = plt.subplots(figsize=(10, 6))
    bins = np.arange(0, 105, 5)

    minority_d = d_i_plot[minority_mask]
    majority_d = d_i_plot[~minority_mask]

    ax.hist(majority_d[~np.isnan(majority_d)], bins=bins, alpha=0.7,
            label=f"Majority (n={np.sum(~np.isnan(majority_d))})", color="blue")
    ax.hist(minority_d[~np.isnan(minority_d)], bins=bins, alpha=0.7,
            label=f"Minority (n={np.sum(~np.isnan(minority_d))})", color="red")

    ax.set_xlabel("Onset Delay (epoch)")
    ax.set_ylabel("Count")
    ax.set_title("Distribution of Onset Delays by Group")
    ax.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_loss_trajectories(loss_history: np.ndarray, minority_mask: np.ndarray,
                          out_path: str, n_samples: int = 20) -> None:
    """Plot sample loss trajectories."""
    fig, ax = plt.subplots(figsize=(12, 6))

    minority_idx = np.where(minority_mask)[0]
    majority_idx = np.where(~minority_mask)[0]

    n_each = n_samples // 2
    np.random.seed(42)
    minority_sample = np.random.choice(minority_idx, min(n_each, len(minority_idx)), replace=False)
    majority_sample = np.random.choice(majority_idx, min(n_each, len(majority_idx)), replace=False)

    epochs = np.arange(loss_history.shape[1])

    for idx in majority_sample:
        ax.plot(epochs, loss_history[idx], color="blue", alpha=0.3, linewidth=0.8)
    for idx in minority_sample:
        ax.plot(epochs, loss_history[idx], color="red", alpha=0.5, linewidth=1.0)

    ax.plot([], [], color="blue", label="Majority")
    ax.plot([], [], color="red", label="Minority")

    ax.set_xlabel("Epoch")
    ax.set_ylabel("Loss")
    ax.set_title("Per-Sample Loss Trajectories")
    ax.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_precision_recall_curve(loss_matrix: np.ndarray, minority_mask: np.ndarray, out_path: str) -> None:
    """PR curve as percentile threshold varies."""
    percentiles = range(50, 100, 2)
    precisions = []
    recalls = []

    loss_at_20 = loss_matrix[:, 20]
    valid_mask = ~np.isnan(loss_at_20)

    for p in percentiles:
        threshold = np.percentile(loss_at_20[valid_mask], p)
        pred = np.zeros(len(minority_mask), dtype=bool)
        pred[valid_mask] = loss_at_20[valid_mask] > threshold
        metrics = compute_gate_metrics(pred, minority_mask)
        precisions.append(metrics["precision"])
        recalls.append(metrics["recall"])

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(list(percentiles), precisions, label="Precision", marker="o", markersize=3)
    ax.plot(list(percentiles), recalls, label="Recall", marker="s", markersize=3)
    ax.axhline(y=0.5, color="gray", linestyle="--", alpha=0.5)
    ax.axhline(y=0.3, color="gray", linestyle=":", alpha=0.5)
    ax.axvline(x=90, color="green", linestyle="-.", label="90th percentile")

    ax.set_xlabel("Loss Percentile Threshold")
    ax.set_ylabel("Score")
    ax.set_title("Precision/Recall vs Loss Percentile Threshold")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def run_evaluation(tracker, minority_mask: np.ndarray, figures_dir: str, T_early: int = 20) -> dict:
    """Run full evaluation and generate figures."""
    import os
    os.makedirs(figures_dir, exist_ok=True)

    d_i = tracker.get_onset_delays()
    loss_history = tracker.get_loss_history()
    pred_minority = tracker.predict_minority(T_early)

    gate_metrics = compute_gate_metrics(pred_minority, minority_mask)
    stat, pvalue = mann_whitney_test(d_i, minority_mask)

    results = {
        "precision": gate_metrics["precision"],
        "recall": gate_metrics["recall"],
        "mann_whitney_stat": stat,
        "mann_whitney_pvalue": pvalue,
        "T_early": T_early,
    }

    plot_gate_metrics_bar(results, os.path.join(figures_dir, "gate_metrics.png"))
    plot_onset_delay_histogram(d_i, minority_mask, os.path.join(figures_dir, "onset_histogram.png"))
    plot_loss_trajectories(loss_history, minority_mask, os.path.join(figures_dir, "loss_trajectories.png"))
    plot_precision_recall_curve(loss_history, minority_mask, os.path.join(figures_dir, "pr_curve.png"))

    return results
