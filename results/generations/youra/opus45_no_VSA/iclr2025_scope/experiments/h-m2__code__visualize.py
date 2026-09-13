"""H-M2 Visualization Suite"""
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path


def plot_gate_metrics(cosine_mean: float, acc_drop: float, path: str) -> None:
    """Bar chart comparing metrics against gate thresholds."""
    from config import COSINE_PASS, ACC_DROP_PASS

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    # Cosine similarity
    ax = axes[0]
    colors = ["green" if cosine_mean >= COSINE_PASS else "orange"]
    ax.bar(["Cosine Mean"], [cosine_mean], color=colors)
    ax.axhline(y=COSINE_PASS, color="red", linestyle="--", label=f"Threshold ({COSINE_PASS})")
    ax.set_ylim(0, 1)
    ax.set_ylabel("Cosine Similarity")
    ax.set_title("Paraphrase Cosine Similarity")
    ax.legend()

    # Accuracy drop
    ax = axes[1]
    colors = ["green" if acc_drop < ACC_DROP_PASS else "orange"]
    ax.bar(["Max Acc Drop"], [acc_drop], color=colors)
    ax.axhline(y=ACC_DROP_PASS, color="red", linestyle="--", label=f"Threshold ({ACC_DROP_PASS})")
    ax.set_ylim(0, 0.5)
    ax.set_ylabel("Accuracy Drop")
    ax.set_title("Masking Accuracy Drop")
    ax.legend()

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_cosine_distribution(cosine_values: list, path: str) -> None:
    """Histogram of cosine similarities."""
    from config import COSINE_PASS, COSINE_FAIL

    plt.figure(figsize=(8, 5))
    plt.hist(cosine_values, bins=50, edgecolor="black", alpha=0.7)
    plt.axvline(x=COSINE_PASS, color="green", linestyle="--", label=f"PASS ({COSINE_PASS})")
    plt.axvline(x=COSINE_FAIL, color="red", linestyle="--", label=f"FAIL ({COSINE_FAIL})")
    plt.xlabel("Cosine Similarity")
    plt.ylabel("Count")
    plt.title("Distribution of Paraphrase Cosine Similarities")
    plt.legend()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_drop_by_perturbation(drops: dict, path: str) -> None:
    """Bar chart of accuracy drop by perturbation type."""
    from config import ACC_DROP_PASS

    names = list(drops.keys())
    values = list(drops.values())
    colors = ["green" if v < ACC_DROP_PASS else "orange" for v in values]

    plt.figure(figsize=(8, 5))
    plt.bar(names, values, color=colors, edgecolor="black")
    plt.axhline(y=ACC_DROP_PASS, color="red", linestyle="--", label=f"Threshold ({ACC_DROP_PASS})")
    plt.xlabel("Perturbation Type")
    plt.ylabel("Accuracy Drop")
    plt.title("Accuracy Drop by Perturbation Type")
    plt.xticks(rotation=45, ha="right")
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_per_class_heatmap(per_class: dict, path: str) -> None:
    """Heatmap of routing consistency per class."""
    if not per_class:
        print("No per-class data for heatmap")
        return

    names = list(per_class.keys())
    values = np.array([[per_class[n]] for n in names])

    plt.figure(figsize=(3, max(6, len(names) * 0.3)))
    sns.heatmap(values, yticklabels=names, xticklabels=["Consistency"],
                annot=True, fmt=".2f", cmap="RdYlGn", vmin=0, vmax=1)
    plt.title("Per-Class Routing Consistency")
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_failure_cases(failures: list, path: str, n: int = 5) -> None:
    """Text render of top-n routing-inconsistent examples."""
    fig, ax = plt.subplots(figsize=(10, min(8, n * 1.5)))
    ax.axis("off")

    text_content = "Top Routing-Inconsistent Examples\n" + "=" * 40 + "\n\n"
    for i, f in enumerate(failures[:n]):
        text_content += f"{i+1}. Original: {f.get('text', 'N/A')[:80]}...\n"
        text_content += f"   Paraphrases: {f.get('paras', 0)}, Consistency: {sum(f.get('consistent', []))/max(len(f.get('consistent', [1])), 1):.2f}\n\n"

    ax.text(0.05, 0.95, text_content, transform=ax.transAxes, fontsize=9,
            verticalalignment="top", fontfamily="monospace")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
