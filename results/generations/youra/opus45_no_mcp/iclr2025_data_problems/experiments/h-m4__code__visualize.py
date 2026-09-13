import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import roc_curve
import os


def plot_ssi_distribution_by_level(ssi_by_level: dict, out_path: str):
    fig, ax = plt.subplots(figsize=(10, 6))
    levels = sorted(ssi_by_level.keys())
    data = [ssi_by_level[lvl] for lvl in levels]
    labels = [f"{lvl}%" for lvl in levels]

    ax.boxplot(data, tick_labels=labels)
    ax.set_xlabel("Contamination Level")
    ax.set_ylabel("SSI (1/variance)")
    ax.set_title("SSI Distribution by Contamination Level")
    ax.set_yscale('log')

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_roc_curve(ssi: np.ndarray, labels: np.ndarray, auc: float, out_path: str):
    fig, ax = plt.subplots(figsize=(8, 8))
    fpr, tpr, _ = roc_curve(labels, ssi)

    ax.plot(fpr, tpr, 'b-', linewidth=2, label=f'ROC (AUC = {auc:.3f})')
    ax.plot([0, 1], [0, 1], 'k--', linewidth=1, label='Random')
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curve: SSI-based Contamination Classification")
    ax.legend(loc='lower right')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_correlation_scatter(pcts: list[float], mean_ssi: list[float], r: float, out_path: str):
    fig, ax = plt.subplots(figsize=(8, 6))

    ax.scatter(pcts, mean_ssi, s=100, c='blue', alpha=0.7)

    z = np.polyfit(pcts, mean_ssi, 1)
    p = np.poly1d(z)
    x_line = np.linspace(min(pcts), max(pcts), 100)
    ax.plot(x_line, p(x_line), 'r--', linewidth=2, label=f'r = {r:.3f}')

    ax.set_xlabel("Contamination Level (%)")
    ax.set_ylabel("Mean SSI")
    ax.set_title("Correlation: Contamination Level vs Mean SSI")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_gate_bar(gate_result: dict, out_path: str):
    fig, ax = plt.subplots(figsize=(10, 6))

    metrics = ['AUC', 'Pearson r', "Cohen's d"]
    values = [gate_result['auc'], gate_result['pearson_r'], abs(gate_result['cohens_d'])]
    thresholds = [gate_result['auc_threshold'], gate_result['r_threshold'], gate_result['d_threshold']]

    x = np.arange(len(metrics))
    width = 0.35

    bars = ax.bar(x - width/2, values, width, label='Measured', color='steelblue')
    ax.bar(x + width/2, thresholds, width, label='Threshold', color='coral', alpha=0.7)

    for i, (v, t) in enumerate(zip(values, thresholds)):
        if v > t:
            bars[i].set_color('green')
        else:
            bars[i].set_color('red')

    ax.set_ylabel('Value')
    ax.set_title(f'Gate Metrics Comparison (Result: {gate_result["gate_result"]})')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.legend()
    ax.axhline(y=0, color='black', linewidth=0.5)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def generate_all_figures(results: dict, ssi_by_level: dict, labels: np.ndarray,
                         ssi_combined: np.ndarray, out_dir: str) -> list[str]:
    os.makedirs(out_dir, exist_ok=True)
    saved = []

    path = os.path.join(out_dir, "ssi_distribution.png")
    plot_ssi_distribution_by_level(ssi_by_level, path)
    saved.append(path)

    path = os.path.join(out_dir, "roc_curve.png")
    plot_roc_curve(ssi_combined, labels, results['auc'], path)
    saved.append(path)

    path = os.path.join(out_dir, "correlation_scatter.png")
    pcts = list(ssi_by_level.keys())
    mean_ssi = [np.mean(ssi_by_level[p]) for p in pcts]
    plot_correlation_scatter(pcts, mean_ssi, results['pearson_r'], path)
    saved.append(path)

    path = os.path.join(out_dir, "gate_metrics.png")
    plot_gate_bar(results, path)
    saved.append(path)

    return saved
