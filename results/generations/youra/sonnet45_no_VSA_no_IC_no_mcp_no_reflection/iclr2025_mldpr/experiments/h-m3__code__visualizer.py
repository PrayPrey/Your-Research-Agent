"""Metrics visualizer for h-m3 experiment."""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List


class MetricsVisualizer:
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)

    def plot_gate_metrics(
        self,
        precision: float,
        recall: float,
        baseline_precision: float = 0.0,
        baseline_recall: float = 0.0,
        target_precision: float = 0.8,
        target_recall: float = 0.7
    ) -> None:
        """Bar chart comparing target vs baseline vs proposed metrics."""
        fig, ax = plt.subplots(figsize=(8, 5))

        models = ['Target', 'Baseline', 'Proposed']
        precision_vals = [target_precision, baseline_precision, precision]
        recall_vals = [target_recall, baseline_recall, recall]

        x = np.arange(len(models))
        width = 0.35

        ax.bar(x - width/2, precision_vals, width, label='Precision', alpha=0.8)
        ax.bar(x + width/2, recall_vals, width, label='Recall', alpha=0.8)

        ax.axhline(y=target_precision, color='r', linestyle='--', linewidth=1, alpha=0.5)
        ax.axhline(y=target_recall, color='b', linestyle='--', linewidth=1, alpha=0.5)

        ax.set_ylabel('Score')
        ax.set_title('Gate Metrics Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(models)
        ax.legend()
        ax.set_ylim([0, 1.1])

        plt.tight_layout()
        plt.savefig(self.output_dir / 'gate_metrics.png', dpi=300)
        plt.close()

    def plot_citation_velocity_timeline(
        self,
        benchmark: str,
        citations_df: pd.DataFrame,
        velocity_series: pd.Series,
        saturation_date: str,
        shift_date: str = None
    ) -> None:
        """Line plot with velocity + event markers."""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

        # Citations plot
        df = citations_df.copy()
        df['date'] = pd.to_datetime(df['date'])
        ax1.plot(df['date'], df['citations'], marker='o', markersize=3)
        ax1.set_ylabel('Citations')
        ax1.set_title(f'{benchmark}: Citation Growth')

        # Velocity plot
        ax2.plot(velocity_series.index, velocity_series.values, marker='o', markersize=3, color='orange')
        ax2.set_ylabel('Citation Velocity')
        ax2.set_xlabel('Date')
        ax2.set_title('Citation Velocity (3-month rolling)')

        # Markers
        sat_dt = pd.to_datetime(saturation_date)
        ax1.axvline(x=sat_dt, color='r', linestyle='--', label='Saturation', alpha=0.7)
        ax2.axvline(x=sat_dt, color='r', linestyle='--', alpha=0.7)

        if shift_date:
            shift_dt = pd.to_datetime(shift_date)
            ax1.axvline(x=shift_dt, color='g', linestyle='--', label='Paradigm Shift', alpha=0.7)
            ax2.axvline(x=shift_dt, color='g', linestyle='--', alpha=0.7)

        ax1.legend()
        plt.tight_layout()
        plt.savefig(self.output_dir / f'timeline_{benchmark}.png', dpi=300)
        plt.close()

    def plot_confusion_matrix(self, y_true: List[int], y_pred: List[int]) -> None:
        """2x2 heatmap with seaborn."""
        from sklearn.metrics import confusion_matrix

        cm = confusion_matrix(y_true, y_pred)
        fig, ax = plt.subplots(figsize=(6, 5))

        sns.heatmap(
            cm, annot=True, fmt='d', cmap='RdBu_r',
            xticklabels=['No Shift', 'Shift'],
            yticklabels=['No Shift', 'Shift'],
            ax=ax
        )

        ax.set_ylabel('True Label')
        ax.set_xlabel('Predicted Label')
        ax.set_title('Confusion Matrix')

        plt.tight_layout()
        plt.savefig(self.output_dir / 'confusion_matrix.png', dpi=300)
        plt.close()
