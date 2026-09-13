"""Results visualization generator."""
import logging
import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, Any


logger = logging.getLogger(__name__)


class ResultsVisualizer:
    """Generate publication-quality visualizations."""

    def __init__(self, style: str = "seaborn-v0_8", figure_dir: str = "figures/"):
        """Initialize visualizer.

        Args:
            style: Matplotlib style to use
            figure_dir: Directory to save figures
        """
        try:
            plt.style.use(style)
        except Exception:
            logger.warning(f"Style {style} not found, using default")

        self.figure_dir = figure_dir
        os.makedirs(figure_dir, exist_ok=True)

    def plot_gate_comparison(
        self,
        target_metrics: Dict[str, float],
        actual_metrics: Dict[str, float],
        gate_status: str
    ):
        """Figure 1 (MANDATORY): Gate metrics bar chart.

        Args:
            target_metrics: Target threshold values
            actual_metrics: Actual measured values
            gate_status: PASS/FAIL/PARTIAL status
        """
        logger.info("Generating gate comparison plot...")

        fig, ax = plt.subplots(figsize=(10, 6))

        metrics = ['rho', 'p_value']
        x = np.arange(len(metrics))
        width = 0.35

        targets = [target_metrics.get(m, 0) for m in metrics]
        actuals = [actual_metrics.get(m, 0) for m in metrics]

        ax.bar(x - width/2, targets, width, label='Target', alpha=0.8)
        ax.bar(x + width/2, actuals, width, label='Actual', alpha=0.8)

        ax.set_xlabel('Metrics')
        ax.set_ylabel('Values')
        ax.set_title(f'Gate Metrics Comparison - Status: {gate_status}')
        ax.set_xticks(x)
        ax.set_xticklabels(metrics)
        ax.legend()

        plt.tight_layout()
        plt.savefig(os.path.join(self.figure_dir, '01_gate_comparison.png'), dpi=300)
        plt.close()

        logger.info("Saved gate comparison plot")

    def plot_correlation_scatter(
        self,
        df: pd.DataFrame,
        rho: float,
        p_value: float
    ):
        """Figure 2: Documentation score vs reproduction rate.

        Args:
            df: DataFrame with data
            rho: Spearman correlation coefficient
            p_value: P-value
        """
        logger.info("Generating correlation scatter plot...")

        fig, ax = plt.subplots(figsize=(10, 6))

        # Add jitter for visualization
        doc_scores = df['doc_score'] + np.random.normal(0, 0.05, len(df))
        reproduced = df['reproduced_within_12m'].astype(int) + np.random.normal(0, 0.02, len(df))

        ax.scatter(doc_scores, reproduced, alpha=0.5)

        # Add trend line
        z = np.polyfit(df['doc_score'], df['reproduced_within_12m'].astype(int), 1)
        p = np.poly1d(z)
        x_line = np.linspace(0, 3, 100)
        ax.plot(x_line, p(x_line), "r--", linewidth=2, label='Trend line')

        ax.set_xlabel('Documentation Score (0-3)')
        ax.set_ylabel('Reproduced within 12 months')
        ax.set_title(f'Documentation vs Reproduction Success\nSpearman ρ = {rho:.3f}, p = {p_value:.4f}')
        ax.legend()

        plt.tight_layout()
        plt.savefig(os.path.join(self.figure_dir, '02_correlation_scatter.png'), dpi=300)
        plt.close()

        logger.info("Saved correlation scatter plot")

    def plot_success_by_doc_level(self, df: pd.DataFrame):
        """Figure 3: Box plot by documentation completeness level.

        Args:
            df: DataFrame with data
        """
        logger.info("Generating success by doc level plot...")

        fig, ax = plt.subplots(figsize=(10, 6))

        # Calculate reproduction rate by doc_score
        rates = df.groupby('doc_score')['reproduced_within_12m'].mean()

        ax.bar(rates.index, rates.values, alpha=0.8)
        ax.set_xlabel('Documentation Score')
        ax.set_ylabel('Reproduction Success Rate')
        ax.set_title('Reproduction Success by Documentation Level')
        ax.set_xticks([0, 1, 2, 3])

        plt.tight_layout()
        plt.savefig(os.path.join(self.figure_dir, '03_success_boxplot.png'), dpi=300)
        plt.close()

        logger.info("Saved success by doc level plot")

    def plot_odds_ratio_forest(self, odds_results: Dict):
        """Figure 4: Forest plot for logistic regression.

        Args:
            odds_results: Dictionary with OR and CI for each predictor
        """
        logger.info("Generating odds ratio forest plot...")

        fig, ax = plt.subplots(figsize=(10, 8))

        predictors = list(odds_results.keys())
        ors = [odds_results[p]['OR'] for p in predictors]
        ci_lowers = [odds_results[p]['CI_lower'] for p in predictors]
        ci_uppers = [odds_results[p]['CI_upper'] for p in predictors]

        y_pos = np.arange(len(predictors))

        ax.errorbar(ors, y_pos, xerr=[[or_val - ci_l for or_val, ci_l in zip(ors, ci_lowers)],
                                       [ci_u - or_val for or_val, ci_u in zip(ors, ci_uppers)]],
                   fmt='o', markersize=8, capsize=5)

        ax.axvline(x=1.0, color='red', linestyle='--', label='OR = 1.0')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(predictors)
        ax.set_xlabel('Odds Ratio')
        ax.set_title('Logistic Regression Odds Ratios (95% CI)')
        ax.legend()

        plt.tight_layout()
        plt.savefig(os.path.join(self.figure_dir, '04_odds_ratio_forest.png'), dpi=300)
        plt.close()

        logger.info("Saved odds ratio forest plot")

    def plot_timeline_by_doc_level(self, df: pd.DataFrame):
        """Figure 5: Reproduction rate over time.

        Args:
            df: DataFrame with data
        """
        logger.info("Generating timeline plot...")

        fig, ax = plt.subplots(figsize=(12, 6))

        for score in [0, 1, 2, 3]:
            subset = df[df['doc_score'] == score]
            if len(subset) > 0:
                rates = subset.groupby('pub_year')['reproduced_within_12m'].mean()
                ax.plot(rates.index, rates.values, marker='o', label=f'Doc Score {score}')

        ax.set_xlabel('Publication Year')
        ax.set_ylabel('Reproduction Success Rate')
        ax.set_title('Reproduction Rate Over Time by Documentation Level')
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(os.path.join(self.figure_dir, '05_timeline_trends.png'), dpi=300)
        plt.close()

        logger.info("Saved timeline plot")

    def generate_all_figures(
        self,
        df: pd.DataFrame,
        analysis_results: Dict[str, Any]
    ):
        """Generate all 5 figures and save to figures/ directory.

        Args:
            df: DataFrame with data
            analysis_results: Dictionary with analysis results
        """
        logger.info("Generating all figures...")

        # Figure 1: Gate comparison
        target_metrics = {'rho': 0.3, 'p_value': 0.01}
        actual_metrics = {
            'rho': analysis_results['rho'],
            'p_value': analysis_results['p_value']
        }
        self.plot_gate_comparison(
            target_metrics,
            actual_metrics,
            analysis_results['gate_status']['status']
        )

        # Figure 2: Correlation scatter
        self.plot_correlation_scatter(
            df,
            analysis_results['rho'],
            analysis_results['p_value']
        )

        # Figure 3: Success by doc level
        self.plot_success_by_doc_level(df)

        # Figure 4: Odds ratio forest
        self.plot_odds_ratio_forest(analysis_results['odds_results'])

        # Figure 5: Timeline
        self.plot_timeline_by_doc_level(df)

        logger.info("All figures generated successfully")
