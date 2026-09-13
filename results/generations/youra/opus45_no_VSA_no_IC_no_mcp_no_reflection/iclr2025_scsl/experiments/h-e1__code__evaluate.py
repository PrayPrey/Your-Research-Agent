"""Evaluation and visualization for H-E1."""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from config import CONFIG


def check_gate(results: dict) -> bool:
    if 10 not in results:
        return False
    spurious = results[10]["spurious_alignment"]
    core = results[10]["core_alignment"]
    return spurious > CONFIG.spurious_gate and core < CONFIG.core_gate


def plot_bar_comparison(results: dict, epochs: list, out_path: str) -> None:
    spurious = [results.get(e, {}).get("spurious_alignment", 0) for e in epochs]
    core = [results.get(e, {}).get("core_alignment", 0) for e in epochs]
    x = range(len(epochs))
    width = 0.35
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar([i - width/2 for i in x], spurious, width, label="Spurious Alignment", color="tab:red")
    ax.bar([i + width/2 for i in x], core, width, label="Core Alignment", color="tab:blue")
    ax.axhline(y=CONFIG.spurious_gate, color="red", linestyle="--", label=f"Spurious Gate ({CONFIG.spurious_gate})")
    ax.axhline(y=CONFIG.core_gate, color="blue", linestyle="--", label=f"Core Gate ({CONFIG.core_gate})")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Alignment")
    ax.set_title("Spurious vs Core Alignment by Epoch")
    ax.set_xticks(list(x))
    ax.set_xticklabels([str(e) for e in epochs])
    ax.legend()
    ax.set_ylim(0, 1)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_alignment_evolution(results: dict, out_path: str) -> None:
    epochs = sorted(results.keys())
    spurious = [results[e]["spurious_alignment"] for e in epochs]
    core = [results[e]["core_alignment"] for e in epochs]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(epochs, spurious, "o-", label="Spurious", color="tab:red")
    ax.plot(epochs, core, "o-", label="Core", color="tab:blue")
    ax.axhline(y=CONFIG.spurious_gate, color="red", linestyle="--", alpha=0.5)
    ax.axhline(y=CONFIG.core_gate, color="blue", linestyle="--", alpha=0.5)
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Alignment")
    ax.set_title("Alignment Evolution Over Training")
    ax.legend()
    ax.set_ylim(0, 1)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_svd_variance(singular_values, out_path: str) -> None:
    if singular_values is None:
        return
    sv = singular_values.cpu().numpy()
    variance = sv ** 2
    variance_ratio = variance / variance.sum()
    cumulative = variance_ratio.cumsum()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(range(len(variance_ratio)), variance_ratio, alpha=0.7, label="Individual")
    ax.plot(range(len(cumulative)), cumulative, "r-", label="Cumulative")
    ax.set_xlabel("Component")
    ax.set_ylabel("Variance Ratio")
    ax.set_title("SVD Variance Explained")
    ax.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
