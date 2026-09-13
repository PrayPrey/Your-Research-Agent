"""Visualization for H-M1: Eigenvalue distributions and sharpness comparison"""

import matplotlib.pyplot as plt
import numpy as np
import os


def plot_eigenvalue_distribution(eig_transformer, eig_mamba, out_path):
    """Histogram overlay of Transformer vs Mamba eigenvalue distributions."""
    fig, ax = plt.subplots(figsize=(10, 6))

    bins = np.linspace(
        min(min(eig_transformer), min(eig_mamba)),
        max(max(eig_transformer), max(eig_mamba)),
        30
    )

    ax.hist(eig_transformer, bins=bins, alpha=0.6, label="Transformer", color="#4C72B0", density=True)
    ax.hist(eig_mamba, bins=bins, alpha=0.6, label="Mamba", color="#DD8452", density=True)

    ax.set_xlabel("Eigenvalue")
    ax.set_ylabel("Density")
    ax.set_title("H-M1: Hessian Eigenvalue Distribution")
    ax.legend()

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")


def plot_sharpness_comparison(sharpness_data, out_path):
    """Bar chart of sharpness values per dataset and model."""
    datasets = list(sharpness_data.keys())
    x = np.arange(len(datasets))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 6))

    transformer_vals = [sharpness_data[d]["transformer"] for d in datasets]
    mamba_vals = [sharpness_data[d]["mamba"] for d in datasets]

    bars1 = ax.bar(x - width/2, transformer_vals, width, label="Transformer", color="#4C72B0")
    bars2 = ax.bar(x + width/2, mamba_vals, width, label="Mamba", color="#DD8452")

    ax.set_xlabel("Dataset")
    ax.set_ylabel("SAM Sharpness")
    ax.set_title("H-M1: Loss Landscape Sharpness Comparison")
    ax.set_xticks(x)
    ax.set_xticklabels(datasets)
    ax.legend()

    for bar in bars1 + bars2:
        height = bar.get_height()
        ax.annotate(f'{height:.4f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=8)

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")


def plot_eigenvalue_spectrum(eig_transformer, eig_mamba, out_path):
    """Log-scale plot of top eigenvalues."""
    fig, ax = plt.subplots(figsize=(10, 6))

    x = range(len(eig_transformer))
    ax.semilogy(x, sorted(eig_transformer, reverse=True), 'o-', label="Transformer", color="#4C72B0", markersize=4)
    ax.semilogy(x[:len(eig_mamba)], sorted(eig_mamba, reverse=True), 's-', label="Mamba", color="#DD8452", markersize=4)

    ax.set_xlabel("Eigenvalue Index (sorted)")
    ax.set_ylabel("Eigenvalue (log scale)")
    ax.set_title("H-M1: Top Eigenvalue Spectrum")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")


def plot_all_figures(results, figures_folder):
    """Generate all H-M1 figures."""
    os.makedirs(figures_folder, exist_ok=True)

    all_eig_trans = []
    all_eig_mamba = []
    sharpness_data = {}

    for dataset in ["gsm8k", "nq"]:
        if dataset in results:
            ds_results = results[dataset]
            if "transformer" in ds_results and "mamba" in ds_results:
                trans = ds_results["transformer"]
                mamba = ds_results["mamba"]

                if "eigenvalues" in trans:
                    all_eig_trans.extend(trans["eigenvalues"])
                if "eigenvalues" in mamba:
                    all_eig_mamba.extend(mamba["eigenvalues"])

                sharpness_data[dataset] = {
                    "transformer": trans.get("sharpness", 0),
                    "mamba": mamba.get("sharpness", 0),
                }

    if all_eig_trans and all_eig_mamba:
        plot_eigenvalue_distribution(
            all_eig_trans, all_eig_mamba,
            os.path.join(figures_folder, "eigenvalue_distribution.png")
        )
        plot_eigenvalue_spectrum(
            all_eig_trans, all_eig_mamba,
            os.path.join(figures_folder, "eigenvalue_spectrum.png")
        )

    if sharpness_data:
        plot_sharpness_comparison(
            sharpness_data,
            os.path.join(figures_folder, "sharpness_comparison.png")
        )
