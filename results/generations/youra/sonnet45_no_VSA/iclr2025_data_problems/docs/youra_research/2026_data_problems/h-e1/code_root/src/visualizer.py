"""Generate visualizations for coupling analysis results."""

import logging
from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt
import seaborn as sns

from .coupling_extractor import CouplingMetrics

logger = logging.getLogger(__name__)


class ResultVisualizer:
    """Generate visualizations for coupling analysis results."""

    def __init__(self, output_dir: Path = Path("./figures")):
        """Initialize visualizer with output directory."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Set style
        sns.set_style("whitegrid")
        plt.rcParams["figure.figsize"] = (10, 6)
        plt.rcParams["figure.dpi"] = 300

    def plot_gate_metrics(
        self, average_cv: float, extraction_rate: float
    ) -> Path:
        """Bar chart comparing actual vs target gate metrics."""
        fig, ax = plt.subplots()

        metrics = ["CV", "Extraction Rate"]
        actual = [average_cv, extraction_rate]
        target = [0.3, 0.95]

        x = range(len(metrics))
        width = 0.35

        ax.bar([i - width/2 for i in x], actual, width, label="Actual", color="steelblue")
        ax.bar([i + width/2 for i in x], target, width, label="Target", color="coral")

        ax.set_xlabel("Metric")
        ax.set_ylabel("Value")
        ax.set_title("Gate Metrics Comparison")
        ax.set_xticks(x)
        ax.set_xticklabels(metrics)
        ax.legend()
        ax.set_ylim(0, 1.1)

        # Add horizontal lines for targets
        ax.axhline(y=0.3, color="coral", linestyle="--", alpha=0.5, label="CV Target")
        ax.axhline(y=0.95, color="coral", linestyle="--", alpha=0.5, label="Extraction Target")

        output_path = self.output_dir / "gate_metrics_comparison.png"
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()

        logger.info(f"Saved gate metrics plot to {output_path}")
        return output_path

    def plot_coupling_distribution(
        self, metrics: List[CouplingMetrics], top_n: int = 20
    ) -> Path:
        """Box plots showing coupling distribution per problem."""
        # Group scores by problem
        problem_scores = {}
        for metric in metrics:
            if metric.problem_id not in problem_scores:
                problem_scores[metric.problem_id] = []
            problem_scores[metric.problem_id].append(metric.coupling_score)

        # Select top N problems by submission count
        top_problems = sorted(
            problem_scores.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:top_n]

        # Create box plot
        fig, ax = plt.subplots(figsize=(14, 6))

        if len(top_problems) == 0:
            ax.text(0.5, 0.5, "No data available", ha="center", va="center")
        else:
            data = [scores for _, scores in top_problems]
            labels = [f"P{i+1}" for i in range(len(top_problems))]

            ax.boxplot(data, labels=labels)
            ax.set_xlabel("Problem ID")
            ax.set_ylabel("Coupling Score")
            ax.set_title(f"Coupling Score Distribution (Top {top_n} Problems)")
            plt.xticks(rotation=45)

        output_path = self.output_dir / "coupling_distribution.png"
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()

        logger.info(f"Saved coupling distribution plot to {output_path}")
        return output_path

    def plot_fan_in_vs_fan_out(self, metrics: List[CouplingMetrics]) -> Path:
        """Scatter plot: fan-in vs fan-out, colored by coupling score."""
        fig, ax = plt.subplots()

        if len(metrics) == 0:
            ax.text(0.5, 0.5, "No data available", ha="center", va="center")
        else:
            fan_ins = [m.fan_in for m in metrics]
            fan_outs = [m.fan_out for m in metrics]
            coupling_scores = [m.coupling_score for m in metrics]

            scatter = ax.scatter(
                fan_ins, fan_outs, c=coupling_scores, cmap="viridis", alpha=0.6, s=50
            )

            ax.set_xlabel("Fan-in (Afferent Coupling)")
            ax.set_ylabel("Fan-out (Efferent Coupling)")
            ax.set_title("Fan-in vs Fan-out Scatter")

            cbar = plt.colorbar(scatter, ax=ax)
            cbar.set_label("Coupling Score")

        output_path = self.output_dir / "fan_in_vs_fan_out_scatter.png"
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()

        logger.info(f"Saved fan-in vs fan-out scatter plot to {output_path}")
        return output_path

    def plot_cv_distribution(self, per_problem_cv: Dict[str, float]) -> Path:
        """Histogram of CV values across problems."""
        fig, ax = plt.subplots()

        if len(per_problem_cv) == 0:
            ax.text(0.5, 0.5, "No data available", ha="center", va="center")
        else:
            cv_values = list(per_problem_cv.values())

            ax.hist(cv_values, bins=20, color="steelblue", edgecolor="black", alpha=0.7)
            ax.axvline(x=0.3, color="red", linestyle="--", linewidth=2, label="CV Threshold (0.3)")
            ax.set_xlabel("Coefficient of Variation (CV)")
            ax.set_ylabel("Number of Problems")
            ax.set_title("CV Distribution Across Problems")
            ax.legend()

        output_path = self.output_dir / "cv_distribution_histogram.png"
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()

        logger.info(f"Saved CV distribution histogram to {output_path}")
        return output_path

    def generate_all_figures(
        self,
        metrics: List[CouplingMetrics],
        per_problem_cv: Dict[str, float],
        average_cv: float,
        extraction_rate: float,
    ) -> Dict[str, Path]:
        """Generate all visualization figures."""
        figures = {}

        # Mandatory figure
        figures["gate_metrics"] = self.plot_gate_metrics(average_cv, extraction_rate)

        # Optional figures
        figures["coupling_distribution"] = self.plot_coupling_distribution(metrics, top_n=20)
        figures["fan_scatter"] = self.plot_fan_in_vs_fan_out(metrics)
        figures["cv_histogram"] = self.plot_cv_distribution(per_problem_cv)

        logger.info(f"Generated {len(figures)} figures")
        return figures
