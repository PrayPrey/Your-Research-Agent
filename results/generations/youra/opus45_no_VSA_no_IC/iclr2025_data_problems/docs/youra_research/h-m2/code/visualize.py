"""Visualization for h-m2 dissociation experiment."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def plot_gate_metrics(results: dict, out_path: str) -> None:
    """Bar chart of F-ratio and Cohen's d vs thresholds."""
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    # F-ratio
    ax = axes[0]
    f_val = results["F_ratio"]
    f_thresh = 4.0
    color = "green" if f_val > f_thresh else "red"
    ax.bar(["F-ratio"], [f_val], color=color, alpha=0.7)
    ax.axhline(f_thresh, color="black", linestyle="--", label=f"Threshold ({f_thresh})")
    ax.set_ylabel("F-ratio")
    ax.set_title(f"F-ratio: {f_val:.2f} ({'PASS' if f_val > f_thresh else 'FAIL'})")
    ax.legend()

    # Cohen's d
    ax = axes[1]
    d_val = results["cohens_d"]
    d_thresh = 0.5
    color = "green" if d_val > d_thresh else "red"
    ax.bar(["Cohen's d"], [d_val], color=color, alpha=0.7)
    ax.axhline(d_thresh, color="black", linestyle="--", label=f"Threshold ({d_thresh})")
    ax.set_ylabel("Cohen's d")
    ax.set_title(f"Cohen's d: {d_val:.2f} ({'PASS' if d_val > d_thresh else 'FAIL'})")
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved gate metrics plot: {out_path}")


def plot_profile_scatter_3d(all_profiles: dict, out_path: str) -> None:
    """3D scatter of mode profiles by method."""
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')

    colors = {"trak": "blue", "tracin": "orange", "kronfluence": "green"}
    markers = {"trak": "o", "tracin": "s", "kronfluence": "^"}

    for method, profiles in all_profiles.items():
        arr = np.stack(profiles)
        ax.scatter(arr[:, 0], arr[:, 1], arr[:, 2],
                   c=colors.get(method, "gray"),
                   marker=markers.get(method, "o"),
                   label=method, s=50, alpha=0.7)

    ax.set_xlabel("Memorization")
    ax.set_ylabel("Transfer")
    ax.set_zlabel("Spurious")
    ax.legend()
    ax.set_title("Mode Profiles by Method (10 seeds each)")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved 3D scatter: {out_path}")


def plot_variance_boxplot(all_profiles: dict, out_path: str) -> None:
    """Box plot of profile values by method and dimension."""
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    dim_names = ["Memorization", "Transfer", "Spurious"]
    methods = list(all_profiles.keys())

    for d, (ax, dim_name) in enumerate(zip(axes, dim_names)):
        data = [[np.stack(all_profiles[m])[:, d] for m in methods]]
        data_flat = [np.stack(all_profiles[m])[:, d] for m in methods]
        ax.boxplot(data_flat, labels=methods)
        ax.set_ylabel("Profile value")
        ax.set_title(dim_name)

    plt.suptitle("Profile Distribution by Method")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved boxplot: {out_path}")


def plot_cohens_d_heatmap(all_profiles: dict, out_path: str) -> None:
    """Heatmap of pairwise Cohen's d."""
    methods = list(all_profiles.keys())
    n = len(all_profiles[methods[0]])

    # Compute d for each pair
    d_matrix = np.zeros((len(methods), len(methods)))

    for i, m1 in enumerate(methods):
        for j, m2 in enumerate(methods):
            if i != j:
                arr1 = np.stack(all_profiles[m1]).flatten()
                arr2 = np.stack(all_profiles[m2]).flatten()
                mean_diff = abs(arr1.mean() - arr2.mean())
                pooled_std = np.sqrt((arr1.var() + arr2.var()) / 2)
                d_matrix[i, j] = mean_diff / (pooled_std + 1e-8)

    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(d_matrix, cmap="YlOrRd")
    ax.set_xticks(range(len(methods)))
    ax.set_yticks(range(len(methods)))
    ax.set_xticklabels(methods)
    ax.set_yticklabels(methods)

    for i in range(len(methods)):
        for j in range(len(methods)):
            ax.text(j, i, f"{d_matrix[i, j]:.2f}", ha="center", va="center")

    plt.colorbar(im, label="Cohen's d")
    ax.set_title("Pairwise Cohen's d")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved heatmap: {out_path}")
