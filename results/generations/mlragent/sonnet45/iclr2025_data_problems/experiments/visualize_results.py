"""
Visualization module for experiment results.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 12


class ResultsVisualizer:
    """Visualize experimental results."""

    def __init__(self, results_file: str = "results.json"):
        """Load results from JSON file."""
        with open(results_file, 'r') as f:
            self.results = json.load(f)

        self.output_dir = Path(".")
        self.output_dir.mkdir(exist_ok=True)

    def plot_training_curves(self):
        """Plot training loss curves for all stages."""
        logger.info("Generating training curves...")

        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        stages = ["pretraining", "instruction_tuning", "alignment"]

        for idx, stage in enumerate(stages):
            ax = axes[idx]

            # Collect losses across runs
            all_losses = []
            for run in self.results["runs"]:
                if stage in run["training_metrics"]:
                    losses = run["training_metrics"][stage]["losses"]
                    all_losses.append(losses)

            if len(all_losses) > 0:
                # Compute mean and std
                max_len = max(len(losses) for losses in all_losses)
                padded_losses = []
                for losses in all_losses:
                    padded = losses + [losses[-1]] * (max_len - len(losses))
                    padded_losses.append(padded)

                losses_array = np.array(padded_losses)
                mean_losses = np.mean(losses_array, axis=0)
                std_losses = np.std(losses_array, axis=0)

                epochs = np.arange(1, len(mean_losses) + 1)

                ax.plot(epochs, mean_losses, linewidth=2, label=stage.replace('_', ' ').title())
                ax.fill_between(epochs,
                               mean_losses - std_losses,
                               mean_losses + std_losses,
                               alpha=0.3)

                ax.set_xlabel('Epoch')
                ax.set_ylabel('Loss')
                ax.set_title(f'{stage.replace("_", " ").title()}')
                ax.grid(True, alpha=0.3)
                ax.legend()

        plt.tight_layout()
        output_file = self.output_dir / "training_curves.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Training curves saved to {output_file}")

    def plot_correlation_comparison(self):
        """Plot correlation with ground truth for different methods."""
        logger.info("Generating correlation comparison...")

        if "aggregated" not in self.results:
            logger.warning("No aggregated results found")
            return

        stages = ["pretraining", "instruction_tuning", "alignment"]
        methods = [m for m in self.results["aggregated"][stages[0]].keys()
                  if m != "ground_truth"]

        fig, ax = plt.subplots(figsize=(12, 6))

        x = np.arange(len(stages))
        width = 0.15
        colors = plt.cm.Set3(np.linspace(0, 1, len(methods)))

        for i, method in enumerate(methods):
            correlations = []
            errors = []

            for stage in stages:
                if method in self.results["aggregated"][stage]:
                    corr = self.results["aggregated"][stage][method].get("mean_correlation", 0)
                    std = self.results["aggregated"][stage][method].get("std_correlation", 0)
                    correlations.append(corr)
                    errors.append(std)
                else:
                    correlations.append(0)
                    errors.append(0)

            offset = width * (i - len(methods) / 2)
            ax.bar(x + offset, correlations, width, yerr=errors,
                  label=method.replace('_', ' ').title(),
                  color=colors[i], alpha=0.8, capsize=5)

        ax.set_xlabel('Training Stage')
        ax.set_ylabel('Spearman Correlation with Ground Truth')
        ax.set_title('Data Valuation Method Performance Across Stages')
        ax.set_xticks(x)
        ax.set_xticklabels([s.replace('_', ' ').title() for s in stages])
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_ylim(-0.5, 1.0)
        ax.axhline(y=0, color='k', linestyle='--', alpha=0.3)

        plt.tight_layout()
        output_file = self.output_dir / "correlation_comparison.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Correlation comparison saved to {output_file}")

    def plot_computation_time(self):
        """Plot computation time for different methods."""
        logger.info("Generating computation time comparison...")

        if "aggregated" not in self.results:
            return

        stages = ["pretraining", "instruction_tuning", "alignment"]
        methods = [m for m in self.results["aggregated"][stages[0]].keys()
                  if m != "ground_truth"]

        fig, ax = plt.subplots(figsize=(12, 6))

        x = np.arange(len(stages))
        width = 0.15
        colors = plt.cm.Set2(np.linspace(0, 1, len(methods)))

        for i, method in enumerate(methods):
            times = []
            errors = []

            for stage in stages:
                if method in self.results["aggregated"][stage]:
                    time = self.results["aggregated"][stage][method].get("mean_time", 0)
                    std = self.results["aggregated"][stage][method].get("std_time", 0)
                    times.append(time)
                    errors.append(std)
                else:
                    times.append(0)
                    errors.append(0)

            offset = width * (i - len(methods) / 2)
            ax.bar(x + offset, times, width, yerr=errors,
                  label=method.replace('_', ' ').title(),
                  color=colors[i], alpha=0.8, capsize=5)

        ax.set_xlabel('Training Stage')
        ax.set_ylabel('Computation Time (seconds)')
        ax.set_title('Computational Efficiency of Valuation Methods')
        ax.set_xticks(x)
        ax.set_xticklabels([s.replace('_', ' ').title() for s in stages])
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_yscale('log')

        plt.tight_layout()
        output_file = self.output_dir / "computation_time.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Computation time comparison saved to {output_file}")

    def plot_value_distributions(self):
        """Plot distributions of data values for different methods."""
        logger.info("Generating value distributions...")

        # Use first run for visualization
        if len(self.results["runs"]) == 0:
            return

        run = self.results["runs"][0]
        stages = ["pretraining", "instruction_tuning", "alignment"]

        fig, axes = plt.subplots(1, 3, figsize=(15, 5))

        for idx, stage in enumerate(stages):
            ax = axes[idx]

            if stage not in run["valuation_results"]:
                continue

            stage_results = run["valuation_results"][stage]

            for method, results in stage_results.items():
                if method == "ground_truth":
                    continue

                if "values" in results:
                    values = np.array(results["values"])

                    # Plot histogram
                    ax.hist(values, bins=20, alpha=0.5,
                           label=method.replace('_', ' ').title(),
                           density=True)

            ax.set_xlabel('Data Value')
            ax.set_ylabel('Density')
            ax.set_title(f'{stage.replace("_", " ").title()}')
            ax.legend()
            ax.grid(True, alpha=0.3)

        plt.tight_layout()
        output_file = self.output_dir / "value_distributions.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Value distributions saved to {output_file}")

    def plot_stage_comparison_radar(self):
        """Create radar chart comparing methods across stages."""
        logger.info("Generating radar chart...")

        if "aggregated" not in self.results:
            return

        stages = ["pretraining", "instruction_tuning", "alignment"]
        methods = [m for m in self.results["aggregated"][stages[0]].keys()
                  if m != "ground_truth" and m != "random_baseline"]

        if len(methods) == 0:
            return

        # Create radar chart
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))

        angles = np.linspace(0, 2 * np.pi, len(stages), endpoint=False).tolist()
        angles += angles[:1]  # Complete the circle

        colors = plt.cm.Set1(np.linspace(0, 1, len(methods)))

        for i, method in enumerate(methods):
            values = []
            for stage in stages:
                if method in self.results["aggregated"][stage]:
                    corr = self.results["aggregated"][stage][method].get("mean_correlation", 0)
                    # Normalize to 0-1 range
                    corr = max(0, min(1, corr))
                    values.append(corr)
                else:
                    values.append(0)

            values += values[:1]  # Complete the circle

            ax.plot(angles, values, 'o-', linewidth=2,
                   label=method.replace('_', ' ').title(),
                   color=colors[i])
            ax.fill(angles, values, alpha=0.15, color=colors[i])

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels([s.replace('_', '\n').title() for s in stages])
        ax.set_ylim(0, 1)
        ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'])
        ax.set_title('Method Performance Across Training Stages\n(Correlation with Ground Truth)',
                    y=1.08, fontsize=14)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        ax.grid(True)

        plt.tight_layout()
        output_file = self.output_dir / "stage_comparison_radar.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Radar chart saved to {output_file}")

    def plot_test_metrics(self):
        """Plot test metrics after each stage."""
        logger.info("Generating test metrics plot...")

        stages = ["pretraining", "instruction_tuning", "alignment"]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        # Collect test losses and perplexities
        all_losses = {stage: [] for stage in stages}
        all_perplexities = {stage: [] for stage in stages}

        for run in self.results["runs"]:
            for stage in stages:
                if stage in run["training_metrics"]:
                    metrics = run["training_metrics"][stage]
                    if "test_loss" in metrics:
                        all_losses[stage].append(metrics["test_loss"])
                    if "test_perplexity" in metrics:
                        all_perplexities[stage].append(metrics["test_perplexity"])

        # Plot losses
        x = np.arange(len(stages))
        mean_losses = [np.mean(all_losses[s]) if len(all_losses[s]) > 0 else 0
                      for s in stages]
        std_losses = [np.std(all_losses[s]) if len(all_losses[s]) > 0 else 0
                     for s in stages]

        ax1.bar(x, mean_losses, yerr=std_losses, capsize=5, alpha=0.7, color='skyblue')
        ax1.set_xlabel('Training Stage')
        ax1.set_ylabel('Test Loss')
        ax1.set_title('Test Loss After Each Stage')
        ax1.set_xticks(x)
        ax1.set_xticklabels([s.replace('_', '\n').title() for s in stages])
        ax1.grid(True, alpha=0.3, axis='y')

        # Plot perplexities
        mean_perps = [np.mean(all_perplexities[s]) if len(all_perplexities[s]) > 0 else 0
                     for s in stages]
        std_perps = [np.std(all_perplexities[s]) if len(all_perplexities[s]) > 0 else 0
                    for s in stages]

        ax2.bar(x, mean_perps, yerr=std_perps, capsize=5, alpha=0.7, color='lightcoral')
        ax2.set_xlabel('Training Stage')
        ax2.set_ylabel('Test Perplexity')
        ax2.set_title('Test Perplexity After Each Stage')
        ax2.set_xticks(x)
        ax2.set_xticklabels([s.replace('_', '\n').title() for s in stages])
        ax2.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        output_file = self.output_dir / "test_metrics.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Test metrics saved to {output_file}")

    def generate_all_plots(self):
        """Generate all visualization plots."""
        logger.info("Generating all visualizations...")

        try:
            self.plot_training_curves()
        except Exception as e:
            logger.error(f"Error plotting training curves: {e}")

        try:
            self.plot_correlation_comparison()
        except Exception as e:
            logger.error(f"Error plotting correlation comparison: {e}")

        try:
            self.plot_computation_time()
        except Exception as e:
            logger.error(f"Error plotting computation time: {e}")

        try:
            self.plot_value_distributions()
        except Exception as e:
            logger.error(f"Error plotting value distributions: {e}")

        try:
            self.plot_stage_comparison_radar()
        except Exception as e:
            logger.error(f"Error plotting radar chart: {e}")

        try:
            self.plot_test_metrics()
        except Exception as e:
            logger.error(f"Error plotting test metrics: {e}")

        logger.info("All visualizations generated!")


def main():
    """Main entry point."""
    logging.basicConfig(level=logging.INFO)

    visualizer = ResultsVisualizer("results.json")
    visualizer.generate_all_plots()


if __name__ == "__main__":
    main()
