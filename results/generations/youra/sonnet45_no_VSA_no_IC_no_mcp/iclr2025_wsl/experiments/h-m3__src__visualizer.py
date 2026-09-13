"""Visualization for gate metrics, confusion matrix, domain breakdown."""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Dict, List


class Visualizer:
    """Generate figures for h-m3 validation."""

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def plot_gate_comparison(
        self,
        baseline_precision: float,
        proposed_precision: float,
        threshold: float,
        filename: str,
    ) -> str:
        """Bar chart of baseline vs proposed vs threshold. Returns: saved file path."""
        fig, ax = plt.subplots(figsize=(8, 6))

        labels = ["Baseline\n(Random)", "Proposed\n(Pattern Detector)"]
        values = [baseline_precision, proposed_precision]
        colors = ["gray", "blue"]

        x_pos = np.arange(len(labels))
        bars = ax.bar(x_pos, values, color=colors, alpha=0.7)

        ax.axhline(
            y=threshold, color="red", linestyle="--", linewidth=2, label="Gate Threshold"
        )

        ax.set_ylabel("Precision", fontsize=12)
        ax.set_title("Gate Metrics Comparison", fontsize=14, fontweight="bold")
        ax.set_xticks(x_pos)
        ax.set_xticklabels(labels)
        ax.set_ylim(0, 1.0)
        ax.legend()

        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + 0.02,
                f"{height:.2f}",
                ha="center",
                va="bottom",
                fontsize=11,
            )

        plt.tight_layout()
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=300)
        plt.close()

        return str(filepath)

    def plot_confusion_matrix(
        self, cm: Dict[str, int], title: str, filename: str
    ) -> str:
        """Heatmap of confusion matrix. Returns: saved file path."""
        fig, ax = plt.subplots(figsize=(6, 6))

        matrix = np.array([[cm["tp"], cm["fn"]], [cm["fp"], cm["tn"]]])

        im = ax.imshow(matrix, cmap="Blues", alpha=0.7)

        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(["Confounded", "Unconfounded"])
        ax.set_yticklabels(["Confounded", "Unconfounded"])
        ax.set_xlabel("Predicted", fontsize=12)
        ax.set_ylabel("True", fontsize=12)
        ax.set_title(title, fontsize=14, fontweight="bold")

        for i in range(2):
            for j in range(2):
                text = ax.text(
                    j,
                    i,
                    matrix[i, j],
                    ha="center",
                    va="center",
                    color="black",
                    fontsize=14,
                )

        plt.colorbar(im, ax=ax)
        plt.tight_layout()
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=300)
        plt.close()

        return str(filepath)

    def plot_domain_breakdown(
        self, test_set: List[Dict], predictions: List[str], filename: str
    ) -> str:
        """Precision by domain (NLP, vision, training). Returns: saved file path."""
        domains = ["nlp", "vision", "training"]
        precisions = []

        for domain in domains:
            domain_indices = [
                i for i, sample in enumerate(test_set) if sample["domain"] == domain
            ]
            y_true_domain = [test_set[i]["label"] for i in domain_indices]
            y_pred_domain = [predictions[i] for i in domain_indices]

            tp = sum(
                1
                for t, p in zip(y_true_domain, y_pred_domain)
                if t == "confounded" and p == "confounded"
            )
            fp = sum(
                1
                for t, p in zip(y_true_domain, y_pred_domain)
                if t == "unconfounded" and p == "confounded"
            )

            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            precisions.append(precision)

        fig, ax = plt.subplots(figsize=(8, 6))
        colors = ["skyblue", "lightcoral", "lightgreen"]

        x_pos = np.arange(len(domains))
        bars = ax.bar(x_pos, precisions, color=colors, alpha=0.7)

        ax.set_ylabel("Precision", fontsize=12)
        ax.set_title("Domain-Specific Performance", fontsize=14, fontweight="bold")
        ax.set_xticks(x_pos)
        ax.set_xticklabels([d.upper() for d in domains])
        ax.set_ylim(0, 1.0)

        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + 0.02,
                f"{height:.2f}",
                ha="center",
                va="bottom",
                fontsize=11,
            )

        plt.tight_layout()
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=300)
        plt.close()

        return str(filepath)
