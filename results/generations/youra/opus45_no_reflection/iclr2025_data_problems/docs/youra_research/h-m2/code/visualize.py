import matplotlib.pyplot as plt
import numpy as np
import os

def plot_gate_comparison(bert_metrics, gpt2_metrics, out_path):
    """Bar chart comparing BERT vs GPT-2 spectral metrics."""
    metrics = ["top_eigenvalue", "eigenvalue_ratio", "trace"]
    bert_vals = [bert_metrics.get(m, 0) for m in metrics]
    gpt2_vals = [gpt2_metrics.get(m, 0) for m in metrics]

    x = np.arange(len(metrics))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x - width/2, bert_vals, width, label="BERT", color="#1f77b4")
    ax.bar(x + width/2, gpt2_vals, width, label="GPT-2", color="#ff7f0e")

    ax.set_xlabel("Metric")
    ax.set_ylabel("Value")
    ax.set_title("Hessian Spectrum: BERT vs GPT-2")
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.legend()
    ax.set_yscale("log")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

def plot_eigenvalue_spectrum(bert_eigs, gpt2_eigs, out_path):
    """Plot top-k eigenvalues for both models (log scale)."""
    fig, ax = plt.subplots(figsize=(10, 6))

    x_bert = range(1, len(bert_eigs) + 1)
    x_gpt2 = range(1, len(gpt2_eigs) + 1)

    ax.semilogy(x_bert, sorted(bert_eigs, reverse=True), "o-", label="BERT", markersize=6)
    ax.semilogy(x_gpt2, sorted(gpt2_eigs, reverse=True), "s-", label="GPT-2", markersize=6)

    ax.set_xlabel("Eigenvalue Index")
    ax.set_ylabel("Eigenvalue (log scale)")
    ax.set_title("Top-20 Hessian Eigenvalues")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

def plot_spectral_density(bert_density, gpt2_density, out_path):
    """Plot spectral density comparison."""
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(bert_density[1], bert_density[0], "-", label="BERT", linewidth=2)
    ax.plot(gpt2_density[1], gpt2_density[0], "-", label="GPT-2", linewidth=2)

    ax.set_xlabel("Eigenvalue")
    ax.set_ylabel("Density")
    ax.set_title("Spectral Density Comparison")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
