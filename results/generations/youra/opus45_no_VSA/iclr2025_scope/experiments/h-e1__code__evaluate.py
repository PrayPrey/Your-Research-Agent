"""H-E1 Evaluation - Baselines and visualization"""
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.manifold import TSNE
from typing import List
import os


def random_baseline(labels: List[int], num_classes: int, random_state: int = 42) -> float:
    """Random selection baseline accuracy."""
    np.random.seed(random_state)
    random_preds = np.random.randint(0, num_classes, size=len(labels))
    return np.mean(random_preds == np.array(labels))


def majority_baseline(train_labels: List[int], test_labels: List[int]) -> float:
    """Majority class baseline - always predict most frequent train label."""
    majority_class = max(set(train_labels), key=train_labels.count)
    return np.mean(np.array(test_labels) == majority_class)


def plot_gate_metrics(top1: float, top3: float, out_path: str) -> None:
    """Bar chart comparing top-1/top-3 accuracy vs gate thresholds."""
    fig, ax = plt.subplots(figsize=(8, 6))

    metrics = ["Top-1 Accuracy", "Top-3 Accuracy"]
    values = [top1, top3]
    thresholds = [0.70, 0.85]

    x = np.arange(len(metrics))
    width = 0.35

    bars = ax.bar(x, values, width, label="Achieved", color=["#4CAF50" if v >= t else "#F44336" for v, t in zip(values, thresholds)])
    ax.bar(x + width, thresholds, width, label="Threshold", color="#9E9E9E", alpha=0.5)

    ax.set_ylabel("Accuracy")
    ax.set_title("H-E1 Gate Metrics: Linear Probe Adapter Selection")
    ax.set_xticks(x + width / 2)
    ax.set_xticklabels(metrics)
    ax.legend()
    ax.set_ylim(0, 1.0)

    for bar, val in zip(bars, values):
        ax.annotate(f"{val:.1%}", xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    ha="center", va="bottom", fontsize=10, fontweight="bold")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved gate metrics plot: {out_path}")


def plot_confusion_matrix(y_true: List[int], y_pred: List[int], class_names: List[str], out_path: str) -> None:
    """Confusion matrix heatmap."""
    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(10, 8))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)
    disp.plot(ax=ax, cmap="Blues", values_format="d")
    ax.set_title("H-E1: Adapter/Task Selection Confusion Matrix")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved confusion matrix: {out_path}")


def plot_per_class_accuracy(y_true: List[int], y_pred: List[int], class_names: List[str], out_path: str) -> None:
    """Per-class accuracy breakdown bar chart."""
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    accuracies = []
    for i in range(len(class_names)):
        mask = y_true == i
        if mask.sum() > 0:
            acc = (y_pred[mask] == i).mean()
        else:
            acc = 0.0
        accuracies.append(acc)

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(class_names, accuracies, color="#2196F3")
    ax.axhline(y=0.70, color="green", linestyle="--", label="Threshold (70%)")
    ax.set_ylabel("Accuracy")
    ax.set_xlabel("Task Family / Adapter")
    ax.set_title("H-E1: Per-Class Selection Accuracy")
    ax.set_ylim(0, 1.0)
    ax.legend()
    plt.xticks(rotation=45, ha="right")

    for bar, val in zip(bars, accuracies):
        ax.annotate(f"{val:.0%}", xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved per-class accuracy: {out_path}")


def plot_embedding_tsne(embeddings: np.ndarray, labels: List[int], class_names: List[str], out_path: str) -> None:
    """t-SNE visualization of embeddings colored by class."""
    print("Computing t-SNE (this may take a moment)...")
    tsne = TSNE(n_components=2, random_state=42, perplexity=30)
    coords = tsne.fit_transform(embeddings)

    fig, ax = plt.subplots(figsize=(10, 8))
    scatter = ax.scatter(coords[:, 0], coords[:, 1], c=labels, cmap="tab10", alpha=0.6, s=10)

    handles = [plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=plt.cm.tab10(i / 10), markersize=8, label=name)
               for i, name in enumerate(class_names)]
    ax.legend(handles=handles, title="Task Family", loc="best")
    ax.set_title("H-E1: t-SNE of MiniLM Embeddings by Task/Adapter Class")
    ax.set_xlabel("t-SNE 1")
    ax.set_ylabel("t-SNE 2")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved t-SNE plot: {out_path}")
