import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Dict, List


class HealthMetricsVisualizer:
    def __init__(self, figures_dir: Path):
        self.figures_dir = Path(figures_dir)
        self.figures_dir.mkdir(parents=True, exist_ok=True)

    def plot_gate_metrics(self, report: Dict) -> None:
        fig, ax = plt.subplots(figsize=(10, 6))

        metrics = ['Precision', 'Recall']
        actual = [report['precision'], report['recall']]
        target = [0.6, 0.8]

        x = np.arange(len(metrics))
        width = 0.35

        ax.bar(x - width/2, target, width, label='Target', color='lightblue')
        ax.bar(x + width/2, actual, width, label='Actual', color='steelblue')

        ax.set_ylabel('Score')
        ax.set_title('Gate Metrics: Precision and Recall')
        ax.set_xticks(x)
        ax.set_xticklabels(metrics)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.figures_dir / 'gate_metrics.png', dpi=100)
        plt.close()

    def plot_health_metrics_distribution(self, metrics_df: pd.DataFrame) -> None:
        fig, ax = plt.subplots(figsize=(10, 6))

        scatter = ax.scatter(
            metrics_df['velocity'],
            metrics_df['emergence'],
            c=metrics_df['issue_ratio'],
            cmap='viridis',
            alpha=0.6,
            s=50
        )

        ax.set_xlabel('Usage Velocity (slope)')
        ax.set_ylabel('Successor Emergence (count)')
        ax.set_title('Health Metrics Distribution')
        ax.axvline(x=0.3, color='red', linestyle='--', alpha=0.5, label='Velocity threshold')
        ax.axhline(y=3, color='red', linestyle='--', alpha=0.5, label='Emergence threshold')
        ax.legend()
        ax.grid(alpha=0.3)

        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Issue Ratio')

        plt.tight_layout()
        plt.savefig(self.figures_dir / 'health_metrics_distribution.png', dpi=100)
        plt.close()

    def plot_confusion_matrix(self, cm: Dict[str, int]) -> None:
        fig, ax = plt.subplots(figsize=(8, 6))

        matrix = [[cm['tn'], cm['fp']], [cm['fn'], cm['tp']]]
        im = ax.imshow(matrix, cmap='Blues')

        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(['Predicted Negative', 'Predicted Positive'])
        ax.set_yticklabels(['Actual Negative', 'Actual Positive'])

        for i in range(2):
            for j in range(2):
                text = ax.text(j, i, matrix[i][j], ha="center", va="center", color="black", fontsize=20)

        ax.set_title('Confusion Matrix')
        plt.tight_layout()
        plt.savefig(self.figures_dir / 'confusion_matrix.png', dpi=100)
        plt.close()

    def plot_threshold_sensitivity(self, metrics_df: pd.DataFrame, ground_truth: Dict) -> None:
        fig, ax = plt.subplots(figsize=(10, 6))

        velocity_thresholds = np.linspace(-1, 2, 20)
        precisions = []
        recalls = []

        for thresh in velocity_thresholds:
            y_true = [ground_truth.get(ds, False) for ds in metrics_df['dataset_id']]
            y_pred = (
                (metrics_df['velocity'] < thresh) &
                (metrics_df['emergence'] > 3) &
                (metrics_df['issue_ratio'] > 0.6)
            ).tolist()

            if sum(y_pred) > 0:
                tp = sum(1 for t, p in zip(y_true, y_pred) if t and p)
                fp = sum(1 for t, p in zip(y_true, y_pred) if not t and p)
                fn = sum(1 for t, p in zip(y_true, y_pred) if t and not p)

                precision = tp / (tp + fp) if (tp + fp) > 0 else 0
                recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            else:
                precision = 0
                recall = 0

            precisions.append(precision)
            recalls.append(recall)

        ax.plot(velocity_thresholds, precisions, label='Precision', marker='o', markersize=3)
        ax.plot(velocity_thresholds, recalls, label='Recall', marker='s', markersize=3)
        ax.axvline(x=0.3, color='red', linestyle='--', alpha=0.5, label='Current threshold')
        ax.set_xlabel('Velocity Threshold')
        ax.set_ylabel('Score')
        ax.set_title('Threshold Sensitivity Analysis')
        ax.legend()
        ax.grid(alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.figures_dir / 'threshold_sensitivity.png', dpi=100)
        plt.close()

    def plot_deprecation_timeline(self, ground_truth: Dict) -> None:
        fig, ax = plt.subplots(figsize=(10, 6))

        months = list(range(7))
        deprecation_events = [gt for gt in ground_truth.values() if gt]
        total_deprecated = len(deprecation_events)

        cumulative = [0]
        for month in range(1, 7):
            cumulative.append(int(total_deprecated * (month / 6)))

        ax.plot(months, cumulative, marker='o', linewidth=2, markersize=8)
        ax.set_xlabel('Month')
        ax.set_ylabel('Cumulative Deprecations')
        ax.set_title('Deprecation Timeline (6 months)')
        ax.grid(alpha=0.3)
        ax.set_xticks(months)

        plt.tight_layout()
        plt.savefig(self.figures_dir / 'deprecation_timeline.png', dpi=100)
        plt.close()
