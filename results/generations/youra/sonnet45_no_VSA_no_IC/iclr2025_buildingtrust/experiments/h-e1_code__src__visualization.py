"""Visualization for coupling analysis results."""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_coupling_heatmap(phi_matrix, dimensions, model_name, output_path):
    """Plot phi coefficient heatmap for a single model.

    Args:
        phi_matrix: [5, 5] symmetric phi coefficient matrix
        dimensions: Dimension names for axis labels
        model_name: Model name for title
        output_path: Save path (e.g., 'figures/heatmap_gpt-4.png')
    """
    plt.figure(figsize=(8, 6))
    sns.heatmap(
        phi_matrix,
        annot=True,
        fmt=".3f",
        cmap="coolwarm",
        center=0,
        xticklabels=dimensions,
        yticklabels=dimensions,
        vmin=0,
        vmax=1
    )
    plt.title(f"Coupling Heatmap: {model_name}")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()

def plot_significance_scatter(results, output_path):
    """Scatter plot of phi vs p-value for all model-pair combinations.

    Args:
        results: DataFrame with columns [model, dim1, dim2, phi, p_value]
        output_path: Save path (e.g., 'figures/significance_scatter.png')

    Plot:
        x-axis: phi coefficient
        y-axis: -log10(p_value)
        Horizontal line at p=0.01
        Vertical line at phi=0.3
    """
    plt.figure(figsize=(10, 6))

    for model in results["model"].unique():
        model_data = results[results["model"] == model]
        plt.scatter(
            model_data["phi"],
            -np.log10(model_data["p_value"]),
            label=model,
            alpha=0.6,
            s=50
        )

    # Reference lines
    plt.axhline(y=-np.log10(0.01), color='red', linestyle='--', label='p=0.01 threshold')
    plt.axvline(x=0.3, color='green', linestyle='--', label='phi=0.3 threshold')

    plt.xlabel("Phi Coefficient")
    plt.ylabel("-log10(p-value)")
    plt.title("Coupling Significance Scatter Plot")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()

def plot_gate_metrics(results, output_path):
    """Bar plot showing gate condition metrics.

    Args:
        results: {
            'significant_pairs': [(model, dim1, dim2, phi, p), ...],
            'max_phi_per_model': {model: phi},
            'gate_pass': bool
        }
        output_path: Save path (e.g., 'figures/gate_metrics.png')
    """
    max_phi_per_model = results["max_phi_per_model"]

    plt.figure(figsize=(8, 5))
    models = list(max_phi_per_model.keys())
    phi_values = list(max_phi_per_model.values())

    bars = plt.bar(models, phi_values)

    # Color bars based on threshold
    for i, phi in enumerate(phi_values):
        if phi >= 0.3:
            bars[i].set_color('green')
        else:
            bars[i].set_color('red')

    plt.axhline(y=0.3, color='blue', linestyle='--', label='phi=0.3 threshold')
    plt.ylabel("Max Phi Coefficient")
    plt.title(f"Gate Metrics (Pass: {results['gate_pass']})")
    plt.legend()
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
