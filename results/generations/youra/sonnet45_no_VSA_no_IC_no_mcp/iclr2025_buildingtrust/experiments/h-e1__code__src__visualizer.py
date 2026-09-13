"""Visualization utilities for entropy distributions."""
import matplotlib.pyplot as plt
import seaborn as sns


def plot_violin(entity_entropies, non_entity_entropies, p_value, save_path):
    """Violin plot comparing distributions."""
    data = []
    labels = []

    for e in entity_entropies:
        data.append(e)
        labels.append("Entity Error")

    for e in non_entity_entropies:
        data.append(e)
        labels.append("Non-Entity Error")

    plt.figure(figsize=(8, 6))
    sns.violinplot(x=labels, y=data, order=["Entity Error", "Non-Entity Error"])
    plt.ylabel("Attention Entropy")
    plt.title(f"Attention Entropy Distributions (p={p_value:.4f})")
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_histograms(entity_entropies, non_entity_entropies, save_path):
    """Overlapping histograms."""
    plt.figure(figsize=(8, 6))
    plt.hist(entity_entropies, bins=15, alpha=0.6, label="Entity Error")
    plt.hist(non_entity_entropies, bins=15, alpha=0.6, label="Non-Entity Error")
    plt.xlabel("Attention Entropy")
    plt.ylabel("Frequency")
    plt.title("Entropy Distribution Comparison")
    plt.legend()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()
