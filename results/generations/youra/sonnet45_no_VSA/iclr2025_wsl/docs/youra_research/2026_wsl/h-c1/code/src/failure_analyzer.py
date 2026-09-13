"""Failure Mode Analyzer - characterizes misclassifications"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import logging
from sklearn.metrics import confusion_matrix

logger = logging.getLogger(__name__)


class FailureModeAnalyzer:
    def __init__(self):
        self.family_order = ['NormFree', 'SENet', 'RegNet', 'ViT-Extreme']

    def generate_confusion_matrix(
        self,
        predictions_df: pd.DataFrame,
        output_path: str
    ) -> np.ndarray:
        """Generate confusion matrix for edge cases.

        Args:
            predictions_df: [N, 4] from EdgeCaseEvaluator
            output_path: PNG output path

        Returns:
            confusion_matrix: [M, M] where M = num unique families
        """
        y_true = predictions_df['ground_truth'].values
        y_pred = predictions_df['predicted_family'].values

        # Get unique labels
        labels = sorted(set(y_true) | set(y_pred))

        cm = confusion_matrix(y_true, y_pred, labels=labels)

        # Plot
        plt.figure(figsize=(10, 8))
        sns.heatmap(
            cm,
            annot=True,
            fmt='d',
            cmap='Blues',
            xticklabels=labels,
            yticklabels=labels
        )
        plt.ylabel('True Edge Family')
        plt.xlabel('Predicted Family')
        plt.title('Edge Case Confusion Matrix')
        plt.tight_layout()
        plt.savefig(output_path, dpi=300)
        plt.close()

        logger.info(f"Confusion matrix saved to {output_path}")
        return cm

    def analyze_feature_distributions(
        self,
        edge_features_df: pd.DataFrame,
        baseline_features_df: pd.DataFrame,
        feature_names: list,
        output_path: str
    ):
        """Compare edge vs baseline feature distributions.

        Args:
            edge_features_df: Edge case features
            baseline_features_df: Baseline features
            feature_names: List of feature column names
            output_path: PNG output path
        """
        fig, axes = plt.subplots(1, len(feature_names), figsize=(16, 4))

        for i, feature in enumerate(feature_names):
            edge_vals = edge_features_df[feature].values
            baseline_vals = baseline_features_df[feature].values if baseline_features_df is not None else []

            ax = axes[i] if len(feature_names) > 1 else axes

            parts = ax.violinplot(
                [edge_vals] if not len(baseline_vals) else [edge_vals, baseline_vals],
                showmeans=True,
                showextrema=True
            )

            ax.set_title(feature)
            if len(baseline_vals):
                ax.set_xticks([1, 2])
                ax.set_xticklabels(['Edge', 'Baseline'])
            else:
                ax.set_xticks([1])
                ax.set_xticklabels(['Edge'])

        plt.suptitle('Feature Distributions: Edge Cases vs Baseline')
        plt.tight_layout()
        plt.savefig(output_path, dpi=300)
        plt.close()

        logger.info(f"Feature distributions saved to {output_path}")

    def identify_systematic_patterns(
        self,
        predictions_df: pd.DataFrame,
        features_df: pd.DataFrame
    ) -> dict:
        """Identify systematic misclassification patterns.

        Args:
            predictions_df: Predictions with ground truth
            features_df: Features for analysis

        Returns:
            {family: pattern_description}
        """
        patterns = {}
        families = predictions_df['ground_truth'].unique()

        for family in families:
            family_preds = predictions_df[predictions_df['ground_truth'] == family]
            misclassified = family_preds[~family_preds['correct']]

            n_total = len(family_preds)
            n_misclassified = len(misclassified)

            if n_misclassified == 0:
                patterns[family] = 'No failures'
            elif n_misclassified == n_total:
                # All misclassified
                common_pred = misclassified['predicted_family'].mode()
                if len(common_pred) > 0:
                    patterns[family] = f'All {n_misclassified} models misclassified as {common_pred[0]}'
                else:
                    patterns[family] = f'All {n_misclassified} models misclassified (various predictions)'
            else:
                patterns[family] = f'{n_misclassified}/{n_total} partial failures'

        return patterns

    def generate_failure_report(
        self,
        misclassified_df: pd.DataFrame,
        systematic_patterns: dict,
        output_path: str
    ):
        """Generate detailed failure analysis markdown.

        Args:
            misclassified_df: Subset where correct=False
            systematic_patterns: From identify_systematic_patterns()
            output_path: MD output path
        """
        with open(output_path, 'w') as f:
            f.write('# Failure Mode Analysis\n\n')

            f.write('## Overall Statistics\n\n')
            f.write(f'Total misclassified: {len(misclassified_df)}\n\n')

            f.write('## Per-Family Patterns\n\n')
            for family, pattern in systematic_patterns.items():
                f.write(f'### {family}\n\n')
                f.write(f'**Pattern:** {pattern}\n\n')

                family_misclassified = misclassified_df[
                    misclassified_df['ground_truth'] == family
                ]
                if len(family_misclassified) > 0:
                    f.write(f'**Misclassified models:**\n\n')
                    for _, row in family_misclassified.iterrows():
                        f.write(f'- {row["model_name"]}: predicted as {row["predicted_family"]}\n')
                    f.write('\n')

            f.write('## Proposed Extensions\n\n')
            f.write('Based on failure patterns, consider:\n\n')
            if 'NormFree' in systematic_patterns and 'All' in systematic_patterns['NormFree']:
                f.write('- Add weight standardization detection for NormFree models\n')
            f.write('- Add GroupNorm count feature\n')
            f.write('- Add activation function type detection\n')
            f.write('- Retrain classifier with balanced edge case representation\n')

        logger.info(f"Failure analysis report saved to {output_path}")
