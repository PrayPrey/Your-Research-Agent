import matplotlib.pyplot as plt
import numpy as np
import os


def plot_gate_metrics(target_r: float, actual_r: float, out_dir: str):
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(["Target", "Actual"], [target_r, actual_r], color=["gray", "steelblue" if actual_r < target_r else "coral"])
    ax.axhline(y=target_r, color="red", linestyle="--", label=f"Threshold: {target_r}")
    ax.set_ylabel("Pearson r")
    ax.set_title("H-M3 Gate: Correlation Threshold")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "gate_metrics.png"), dpi=150)
    plt.close()


def plot_scatter_variance(rep_variances: np.ndarray, conf_variances: np.ndarray, r_value: float, out_dir: str):
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(rep_variances, conf_variances, alpha=0.5, s=10)
    z = np.polyfit(rep_variances, conf_variances, 1)
    p = np.poly1d(z)
    x_line = np.linspace(rep_variances.min(), rep_variances.max(), 100)
    ax.plot(x_line, p(x_line), "r--", label=f"r={r_value:.3f}")
    ax.set_xlabel("Representation Variance (1 - mean cosine sim)")
    ax.set_ylabel("Confidence Variance")
    ax.set_title("Representation vs Confidence Variance")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "scatter_variance.png"), dpi=150)
    plt.close()


def plot_boxplot_by_mps_group(conf_var_high: np.ndarray, conf_var_low: np.ndarray, out_dir: str):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.boxplot([conf_var_high, conf_var_low], labels=["High MPS\n(Low Rep Var)", "Low MPS\n(High Rep Var)"])
    ax.set_ylabel("Confidence Variance")
    ax.set_title("Confidence Variance by MPS Group")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "boxplot_mps_group.png"), dpi=150)
    plt.close()


def plot_correlation_histogram(r_per_seed: list, out_dir: str):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(range(len(r_per_seed)), r_per_seed, color="steelblue")
    ax.axhline(y=-0.4, color="red", linestyle="--", label="Threshold: -0.4")
    ax.set_xlabel("Seed Index")
    ax.set_ylabel("Pearson r")
    ax.set_title("Correlation Across Seeds")
    ax.set_xticks(range(len(r_per_seed)))
    ax.set_xticklabels([f"Seed {i+1}" for i in range(len(r_per_seed))])
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "correlation_histogram.png"), dpi=150)
    plt.close()


def plot_subject_heatmap(subject_correlations: dict, out_dir: str):
    if not subject_correlations:
        return

    subjects = list(subject_correlations.keys())
    correlations = [subject_correlations[s] for s in subjects]

    sorted_indices = np.argsort(correlations)
    subjects = [subjects[i] for i in sorted_indices]
    correlations = [correlations[i] for i in sorted_indices]

    fig, ax = plt.subplots(figsize=(10, max(6, len(subjects) * 0.25)))
    colors = ["steelblue" if c < 0 else "coral" for c in correlations]
    ax.barh(subjects, correlations, color=colors)
    ax.axvline(x=0, color="black", linewidth=0.5)
    ax.axvline(x=-0.4, color="red", linestyle="--", label="Threshold")
    ax.set_xlabel("Pearson r")
    ax.set_title("Per-Subject Correlation")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "subject_heatmap.png"), dpi=150)
    plt.close()
