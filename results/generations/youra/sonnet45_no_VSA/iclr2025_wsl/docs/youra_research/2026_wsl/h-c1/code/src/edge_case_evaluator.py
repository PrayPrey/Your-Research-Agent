"""Edge Case Evaluator - predicts and computes accuracy metrics"""

import numpy as np
import pandas as pd
import logging
from sklearn.metrics import accuracy_score
from statsmodels.stats.proportion import proportion_confint

logger = logging.getLogger(__name__)


class EdgeCaseEvaluator:
    def __init__(self, classifier, scaler, feature_names):
        self.classifier = classifier
        self.scaler = scaler
        self.feature_names = feature_names

    def predict_edge_cases(self, features_df: pd.DataFrame) -> pd.DataFrame:
        """Apply classifier to edge case features.

        Args:
            features_df: [N, >=5] with feature columns

        Returns:
            predictions_df: [N, 4] with [model_name, predicted_family, ground_truth, correct]
        """
        X = features_df[self.feature_names].values
        X_scaled = self.scaler.transform(X)
        y_pred = self.classifier.predict(X_scaled)

        # Classifier returns string labels directly ('CNN', 'Transformer', 'Hybrid')
        predicted_families = list(y_pred)

        predictions_df = pd.DataFrame({
            'model_name': features_df['model_name'].values,
            'predicted_family': predicted_families,
            'ground_truth': features_df['edge_family'].values,
            'correct': [
                pred == truth
                for pred, truth in zip(predicted_families, features_df['edge_family'].values)
            ]
        })

        return predictions_df

    def compute_overall_accuracy(self, predictions_df: pd.DataFrame) -> dict:
        """Compute overall accuracy with Wilson 95% CI.

        Args:
            predictions_df: Output from predict_edge_cases()

        Returns:
            {accuracy, ci_lower, ci_upper, sample_size}
        """
        n = len(predictions_df)
        n_correct = predictions_df['correct'].sum()
        accuracy = n_correct / n

        # Wilson score confidence interval
        ci_lower, ci_upper = proportion_confint(
            n_correct,
            n,
            alpha=0.05,
            method='wilson'
        )

        logger.info(f"Overall accuracy: {accuracy:.3f} (95% CI: [{ci_lower:.3f}, {ci_upper:.3f}])")

        ci_width = ci_upper - ci_lower
        if ci_width > 0.20:
            logger.warning(f"CI width ({ci_width:.3f}) > 0.20. Consider expanding sample size.")

        return {
            'accuracy': float(accuracy),
            'ci_lower': float(ci_lower),
            'ci_upper': float(ci_upper),
            'sample_size': int(n),
            'correct': int(n_correct)
        }

    def compute_per_family_accuracy(self, predictions_df: pd.DataFrame) -> dict:
        """Compute accuracy breakdown per edge family.

        Args:
            predictions_df: Output from predict_edge_cases()

        Returns:
            {family: {accuracy, correct, total}}
        """
        families = predictions_df['ground_truth'].unique()
        per_family_acc = {}

        for family in families:
            family_preds = predictions_df[predictions_df['ground_truth'] == family]
            n_total = len(family_preds)
            n_correct = family_preds['correct'].sum()
            accuracy = n_correct / n_total if n_total > 0 else 0.0

            per_family_acc[family] = {
                'accuracy': float(accuracy),
                'correct': int(n_correct),
                'total': int(n_total)
            }

            logger.info(f"{family}: {accuracy:.3f} ({n_correct}/{n_total})")

        return per_family_acc

    def evaluate_gate_decision(
        self,
        overall_acc: float,
        per_family_acc: dict,
        threshold: float = 0.70,
        min_passing_families: int = 3
    ) -> tuple:
        """Make SHOULD_WORK gate decision.

        Args:
            overall_acc: Overall accuracy
            per_family_acc: Per-family breakdown
            threshold: Accuracy threshold
            min_passing_families: Minimum families that must pass

        Returns:
            (gate_status, rationale)
        """
        passing_families = sum(
            1 for family_stats in per_family_acc.values()
            if family_stats['accuracy'] >= threshold
        )

        if overall_acc >= threshold:
            return 'PASS', f'Overall accuracy {overall_acc:.1%} >= {threshold:.0%} threshold'
        elif passing_families >= min_passing_families:
            return 'PASS', f'{passing_families}/{len(per_family_acc)} families pass {threshold:.0%} threshold'
        else:
            return 'DOCUMENT', (
                f'Overall {overall_acc:.1%} < {threshold:.0%}, '
                f'only {passing_families}/{len(per_family_acc)} families pass'
            )
