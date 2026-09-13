import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from typing import Dict, Any


def plot_complexity_comparison(
    waterbirds_results: Dict[str, Any],
    celeba_results: Dict[str, Any],
    gate_result: Dict[str, Any],
    figures_dir: str,
) -> str:
    os.makedirs(figures_dir, exist_ok=True)
    metrics = ["fft", "variance", "separability"]
    metric_labels = ["FFT Mean Freq", "Intra-class Var", "Separability AUC"]
    datasets = [("Waterbirds", waterbirds_results), ("CelebA", celeba_results)]

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for ax, metric, label in zip(axes, metrics, metric_labels):
        x = np.arange(len(datasets))
        spurious_vals, core_vals, p_vals = [], [], []
        for _, res in datasets:
            m = res.get(metric, {})
            if metric == "fft":
                spurious_vals.append(m.get("spurious_mean_freq", 0))
                core_vals.append(m.get("core_mean_freq", 0))
            elif metric == "variance":
                spurious_vals.append(m.get("var_spurious", 0))
                core_vals.append(m.get("var_core", 0))
            else:
                spurious_vals.append(m.get("spurious_auc", 0))
                core_vals.append(m.get("core_auc", 0))
            p_vals.append(m.get("p_value", 1.0))

        width = 0.35
        bars_s = ax.bar(x - width / 2, spurious_vals, width, label="Spurious", color="coral")
        bars_c = ax.bar(x + width / 2, core_vals, width, label="Core", color="steelblue")

        for i, (p, xs) in enumerate(zip(p_vals, x)):
            y_max = max(spurious_vals[i], core_vals[i])
            sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
            ax.text(xs, y_max * 1.05, f"p={p:.3f}\n{sig}", ha="center", fontsize=8)

        ax.set_xticks(x)
        ax.set_xticklabels([d[0] for d in datasets])
        ax.set_title(label)
        ax.legend()
        ax.set_ylabel("Complexity")

    gate_str = gate_result.get("gate_label", "?")
    fig.suptitle(f"Spurious vs. Core Feature Complexity (Gate: {gate_str})", fontsize=13)
    plt.tight_layout()
    path = os.path.join(figures_dir, "complexity_comparison.png")
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def plot_fft_spectrum(
    spurious_patches: np.ndarray,
    core_patches: np.ndarray,
    figures_dir: str,
    n_examples: int = 4,
) -> str:
    os.makedirs(figures_dir, exist_ok=True)
    n = min(n_examples, len(spurious_patches), len(core_patches))
    fig, axes = plt.subplots(2, n * 2, figsize=(4 * n, 4))

    for i in range(n):
        for j, (patches, label) in enumerate([(spurious_patches, "Spurious"), (core_patches, "Core")]):
            patch = patches[i]
            gray = (0.299 * patch[:, :, 0] + 0.587 * patch[:, :, 1] + 0.114 * patch[:, :, 2]).astype(float)
            F = np.fft.fftshift(np.fft.fft2(gray))
            power = np.log1p(np.abs(F) ** 2)

            col = i * 2 + j
            axes[0, col].imshow(patch)
            axes[0, col].set_title(f"{label} {i+1}")
            axes[0, col].axis("off")
            axes[1, col].imshow(power, cmap="viridis")
            axes[1, col].set_title("FFT Power")
            axes[1, col].axis("off")

    plt.tight_layout()
    path = os.path.join(figures_dir, "fft_spectrum.png")
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def plot_learning_curves(
    waterbirds_sep: Dict,
    celeba_sep: Dict,
    figures_dir: str,
) -> str:
    os.makedirs(figures_dir, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    for ax, sep, title in zip(axes, [waterbirds_sep, celeba_sep], ["Waterbirds", "CelebA"]):
        n_list = sep.get("spurious_curve", {}).get("n_samples_list", [])
        sp_accs = sep.get("spurious_curve", {}).get("mean_accs", [])
        co_accs = sep.get("core_curve", {}).get("mean_accs", [])
        sp_std = sep.get("spurious_curve", {}).get("std_accs", [0] * len(sp_accs))
        co_std = sep.get("core_curve", {}).get("std_accs", [0] * len(co_accs))

        if not n_list or not sp_accs:
            ax.text(0.5, 0.5, f"{title}\nNo data available", ha="center", va="center", transform=ax.transAxes)
            ax.set_title(f"Linear Separability — {title}")
            continue

        sp_accs = np.array(sp_accs)
        co_accs = np.array(co_accs)
        sp_std = np.array(sp_std)
        co_std = np.array(co_std)

        n_arr = np.array(n_list, dtype=float)
        if np.all(n_arr > 0):
            ax.set_xscale("log")
        ax.plot(n_list, sp_accs, "o-", color="coral", label="Spurious")
        ax.fill_between(n_list, sp_accs - sp_std, sp_accs + sp_std, alpha=0.2, color="coral")
        ax.plot(n_list, co_accs, "s-", color="steelblue", label="Core")
        ax.fill_between(n_list, co_accs - co_std, co_accs + co_std, alpha=0.2, color="steelblue")
        ax.axhline(0.9, linestyle="--", color="gray", alpha=0.5, label="90% threshold")
        ax.set_xlabel("Training samples (log scale)")
        ax.set_ylabel("Probe accuracy")
        ax.set_title(f"Linear Separability — {title}")
        ax.legend()

    plt.tight_layout()
    path = os.path.join(figures_dir, "learning_curves.png")
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def plot_feature_pca(
    spurious_feats: np.ndarray,
    core_feats: np.ndarray,
    figures_dir: str,
    method: str = "pca",
) -> str:
    os.makedirs(figures_dir, exist_ok=True)
    from sklearn.decomposition import PCA

    n_spur = min(1000, len(spurious_feats))
    n_core = min(1000, len(core_feats))
    rng = np.random.RandomState(42)
    idx_s = rng.choice(len(spurious_feats), n_spur, replace=False)
    idx_c = rng.choice(len(core_feats), n_core, replace=False)

    all_feats = np.concatenate([spurious_feats[idx_s], core_feats[idx_c]], axis=0)
    labels = np.array([0] * n_spur + [1] * n_core)

    pca = PCA(n_components=2, random_state=42)
    proj = pca.fit_transform(all_feats)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(proj[labels == 0, 0], proj[labels == 0, 1], c="coral", alpha=0.3, s=5, label="Spurious")
    ax.scatter(proj[labels == 1, 0], proj[labels == 1, 1], c="steelblue", alpha=0.3, s=5, label="Core")
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.set_title("PCA of Layer-4 Features: Spurious vs. Core")
    ax.legend()
    plt.tight_layout()
    path = os.path.join(figures_dir, "feature_pca.png")
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def plot_complexity_gap(
    waterbirds_results: Dict[str, Any],
    celeba_results: Dict[str, Any],
    figures_dir: str,
) -> str:
    os.makedirs(figures_dir, exist_ok=True)
    from analysis.statistical_tests import compute_complexity_delta_ci

    metrics = ["fft", "variance", "separability"]
    metric_labels = ["FFT Mean Freq", "Intra-class Var", "Separability AUC"]
    datasets = [("Waterbirds", waterbirds_results), ("CelebA", celeba_results)]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, (ds_name, res) in zip(axes, datasets):
        deltas, ci_lows, ci_highs, mlabels = [], [], [], []
        for metric, mlabel in zip(metrics, metric_labels):
            m = res.get(metric, {})
            if metric == "fft":
                s_vals = np.array(m.get("spurious_freqs", [0]))
                c_vals = np.array(m.get("core_freqs", [0]))
            elif metric == "variance":
                s_vals = m.get("per_feature_var_spurious", np.array([0]))
                c_vals = m.get("per_feature_var_core", np.array([0]))
            else:
                s_vals = np.array(m.get("spurious_curve", {}).get("mean_accs", [0]))
                c_vals = np.array(m.get("core_curve", {}).get("mean_accs", [0]))

            ci = compute_complexity_delta_ci(s_vals, c_vals, n_bootstrap=1000)
            deltas.append(ci["delta"])
            ci_lows.append(ci["delta"] - ci["ci_low"])
            ci_highs.append(ci["ci_high"] - ci["delta"])
            mlabels.append(mlabel)

        x = np.arange(len(metrics))
        colors = ["green" if d > 0 else "red" for d in deltas]
        ax.bar(x, deltas, color=colors, alpha=0.7)
        ax.errorbar(x, deltas, yerr=[ci_lows, ci_highs], fmt="none", color="black", capsize=5)
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels(mlabels, rotation=15, ha="right")
        ax.set_title(f"Complexity Gap (core − spurious) — {ds_name}")
        ax.set_ylabel("Delta complexity")

    plt.tight_layout()
    path = os.path.join(figures_dir, "complexity_gap.png")
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def generate_all_figures(
    waterbirds_patches: Dict,
    celeba_patches: Dict,
    spurious_feats: np.ndarray,
    core_feats: np.ndarray,
    waterbirds_results: Dict[str, Any],
    celeba_results: Dict[str, Any],
    gate_result: Dict[str, Any],
    figures_dir: str,
) -> Dict[str, str]:
    paths = {}
    paths["complexity_comparison"] = plot_complexity_comparison(
        waterbirds_results, celeba_results, gate_result, figures_dir
    )
    paths["fft_spectrum"] = plot_fft_spectrum(
        waterbirds_patches["spurious_patches"],
        waterbirds_patches["core_patches"],
        figures_dir,
    )
    wb_sep = waterbirds_results.get("separability", {})
    cb_sep = celeba_results.get("separability", {})
    if wb_sep and cb_sep:
        paths["learning_curves"] = plot_learning_curves(wb_sep, cb_sep, figures_dir)
    paths["feature_pca"] = plot_feature_pca(spurious_feats, core_feats, figures_dir)
    paths["complexity_gap"] = plot_complexity_gap(waterbirds_results, celeba_results, figures_dir)
    return paths
