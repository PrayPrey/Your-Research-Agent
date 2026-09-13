"""H-M2 figure generation: PCA concentration test visualizations."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path


def plot_r2_bar_comparison(results_a: dict, results_d: dict, out_dir: str) -> None:
    """Figure 1: bar chart R²_A vs R²_D with CI error bars, per (k, label)."""
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    labels = list(results_a.keys())
    k_values = sorted(results_a[labels[0]].keys())
    n_k = len(k_values)
    n_l = len(labels)

    fig, axes = plt.subplots(1, n_l, figsize=(5 * n_l, 5), sharey=False)
    if n_l == 1:
        axes = [axes]

    for ax, lname in zip(axes, labels):
        x = np.arange(n_k)
        width = 0.35
        r2_a = [results_a[lname][k]["r2"] for k in k_values]
        ci_a = [results_a[lname][k]["ci"] for k in k_values]
        r2_d = [results_d[lname][k]["r2"] for k in k_values]
        ci_d = [results_d[lname][k]["ci"] for k in k_values]
        err_a = [[r - c[0] for r, c in zip(r2_a, ci_a)], [c[1] - r for r, c in zip(r2_a, ci_a)]]
        err_d = [[r - c[0] for r, c in zip(r2_d, ci_d)], [c[1] - r for r, c in zip(r2_d, ci_d)]]

        ax.bar(x - width / 2, r2_a, width, label="Condition A (raw)", color="#2196F3",
               yerr=err_a, capsize=4, alpha=0.8)
        ax.bar(x + width / 2, r2_d, width, label="Condition D (canonical)", color="#FF9800",
               yerr=err_d, capsize=4, alpha=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels([f"k={k}" for k in k_values])
        ax.set_ylabel("R²")
        ax.set_title(lname.replace("_", " ").title())
        ax.legend(fontsize=8)
        ax.axhline(0, color="gray", linewidth=0.5)

    fig.suptitle("PCA Concentration: R² Comparison (Condition A vs D)", fontsize=12)
    plt.tight_layout()
    out_path = Path(out_dir) / "fig1_r2_bar_comparison.png"
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


def plot_r2_vs_k(results_a: dict, results_d: dict, out_dir: str) -> None:
    """Figure 2: line plot R² vs k per label."""
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    labels = list(results_a.keys())
    k_values = sorted(results_a[labels[0]].keys())

    fig, axes = plt.subplots(1, len(labels), figsize=(5 * len(labels), 4), sharey=False)
    if len(labels) == 1:
        axes = [axes]

    for ax, lname in zip(axes, labels):
        r2_a = [results_a[lname][k]["r2"] for k in k_values]
        r2_d = [results_d[lname][k]["r2"] for k in k_values]
        ax.plot(k_values, r2_a, "o-", label="Condition A", color="#2196F3")
        ax.plot(k_values, r2_d, "s-", label="Condition D", color="#FF9800")
        ax.set_xlabel("k (PCA components)")
        ax.set_ylabel("R²")
        ax.set_title(lname.replace("_", " ").title())
        ax.legend(fontsize=8)
        ax.set_xticks(k_values)

    fig.suptitle("R² vs k: PCA Concentration", fontsize=12)
    plt.tight_layout()
    out_path = Path(out_dir) / "fig2_r2_vs_k.png"
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


def plot_explained_variance(pca_a, pca_d, out_dir: str) -> None:
    """Figure 3: cumulative explained variance ratio, Condition A vs D."""
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    evr_a = np.cumsum(pca_a.explained_variance_ratio_)
    evr_d = np.cumsum(pca_d.explained_variance_ratio_)
    k = len(evr_a)

    plt.figure(figsize=(6, 4))
    plt.plot(range(1, k + 1), evr_a, label="Condition A (raw)", color="#2196F3")
    plt.plot(range(1, k + 1), evr_d, label="Condition D (canonical)", color="#FF9800")
    plt.xlabel("Number of PCs")
    plt.ylabel("Cumulative Explained Variance")
    plt.title("PCA Explained Variance: Condition A vs D")
    plt.legend()
    plt.tight_layout()
    out_path = Path(out_dir) / "fig3_explained_variance.png"
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


def plot_ci_bars(results_a: dict, results_d: dict, k: int, out_dir: str) -> None:
    """Figure 4: horizontal CI bars at k, per label. Visual gate pass/fail."""
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    labels = list(results_a.keys())
    fig, ax = plt.subplots(figsize=(7, 3))

    for i, lname in enumerate(labels):
        r2_a = results_a[lname][k]["r2"]
        ci_a = results_a[lname][k]["ci"]
        r2_d = results_d[lname][k]["r2"]
        ci_d = results_d[lname][k]["ci"]
        y_a = 2 * i + 0.3
        y_d = 2 * i - 0.3
        ax.plot(ci_a, [y_a, y_a], "-", color="#2196F3", linewidth=3)
        ax.plot(r2_a, y_a, "o", color="#2196F3", label="Condition A" if i == 0 else "")
        ax.plot(ci_d, [y_d, y_d], "-", color="#FF9800", linewidth=3)
        ax.plot(r2_d, y_d, "s", color="#FF9800", label="Condition D" if i == 0 else "")

    ax.set_yticks([2 * i for i in range(len(labels))])
    ax.set_yticklabels([l.replace("_", " ") for l in labels])
    ax.set_xlabel("R²")
    ax.set_title(f"Bootstrap 95% CI at k={k} (gate: non-overlapping = PASS)")
    ax.legend(fontsize=8)
    ax.axvline(0, color="gray", linewidth=0.5)
    plt.tight_layout()
    out_path = Path(out_dir) / f"fig4_ci_bars_k{k}.png"
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


def plot_pc1_scatter(
    X_A_test_pca: np.ndarray,
    X_D_test_pca: np.ndarray,
    y_test: np.ndarray,
    label_name: str,
    out_dir: str,
) -> None:
    """Figure 5: PC1 vs property label scatter, Condition A vs D side-by-side."""
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    ax1.scatter(X_A_test_pca[:, 0], y_test, alpha=0.6, color="#2196F3", s=20)
    ax1.set_xlabel("PC1 (Condition A)")
    ax1.set_ylabel(label_name.replace("_", " "))
    ax1.set_title("Condition A (raw)")
    ax2.scatter(X_D_test_pca[:, 0], y_test, alpha=0.6, color="#FF9800", s=20)
    ax2.set_xlabel("PC1 (Condition D)")
    ax2.set_ylabel(label_name.replace("_", " "))
    ax2.set_title("Condition D (canonical)")
    fig.suptitle(f"PC1 vs {label_name.replace('_', ' ')}", fontsize=12)
    plt.tight_layout()
    out_path = Path(out_dir) / f"fig5_pc1_scatter_{label_name}.png"
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


def generate_all_figures(
    results_a: dict,
    results_d: dict,
    pca_a,
    pca_d,
    X_A_test_pca: np.ndarray,
    X_D_test_pca: np.ndarray,
    Y_test: np.ndarray,
    label_names: list,
    out_dir: str,
) -> None:
    plot_r2_bar_comparison(results_a, results_d, out_dir)
    plot_r2_vs_k(results_a, results_d, out_dir)
    plot_explained_variance(pca_a, pca_d, out_dir)
    plot_ci_bars(results_a, results_d, k=20, out_dir=out_dir)
    for i, lname in enumerate(label_names):
        plot_pc1_scatter(X_A_test_pca, X_D_test_pca, Y_test[:, i], lname, out_dir)
