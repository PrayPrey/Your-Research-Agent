import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path


class Visualizer:
    """Generate required and optional figures."""

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def plot_gate_metrics(self, kappa_scores: dict, threshold: float):
        """REQUIRED: Kappa scores vs 0.80 threshold bar chart."""
        fig, ax = plt.subplots(figsize=(10, 6))

        metrics = list(kappa_scores.keys())
        values = list(kappa_scores.values())

        bars = ax.bar(metrics, values, color=["#2E7D32" if v >= threshold else "#C62828" for v in values])
        ax.axhline(y=threshold, color="black", linestyle="--", label=f"Threshold ({threshold})")
        ax.set_ylabel("Agreement Score")
        ax.set_title("Inter-Rater Agreement: Gate Metrics")
        ax.set_ylim(0, 1.0)
        ax.legend()
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(self.output_dir / "gate_metrics.png", dpi=150)
        plt.close()

    def plot_confusion_matrix(self, labels1, labels2, feature_name: str):
        """Optional: Confusion matrix heatmap."""
        from sklearn.metrics import confusion_matrix
        import numpy as np

        unique_labels = sorted(set(labels1 + labels2))
        cm = confusion_matrix(labels1, labels2, labels=unique_labels)

        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=unique_labels, yticklabels=unique_labels, ax=ax)
        ax.set_ylabel("Annotator 1")
        ax.set_xlabel("Annotator 2")
        ax.set_title(f"Confusion Matrix: {feature_name}")
        plt.tight_layout()
        plt.savefig(self.output_dir / f"confusion_matrix_{feature_name}.png", dpi=150)
        plt.close()

    def plot_feature_distribution(self, annotations: pd.DataFrame):
        """Optional: Feature distribution histogram."""
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        # Task type distribution
        annotations["task_type"].value_counts().plot(kind="bar", ax=axes[0], color="#1976D2")
        axes[0].set_title("Task Type Distribution")
        axes[0].set_ylabel("Count")

        # Modality distribution
        annotations["modality"].value_counts().plot(kind="bar", ax=axes[1], color="#388E3C")
        axes[1].set_title("Modality Distribution")
        axes[1].set_ylabel("Count")

        plt.tight_layout()
        plt.savefig(self.output_dir / "feature_distribution.png", dpi=150)
        plt.close()
