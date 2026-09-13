"""Evaluation and visualization module"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from config import FEATURE_NAMES


class ValidationEvaluator:
    """Evaluate classifier on validation set and generate visualizations"""

    def __init__(self, classifier, scaler):
        self.classifier = classifier
        self.scaler = scaler
        self.logger = logging.getLogger(__name__)

    def evaluate(self, X_val: pd.DataFrame, y_val: pd.Series) -> dict:
        """
        Compute validation metrics.

        Args:
            X_val: Validation features
            y_val: True labels

        Returns:
            Dictionary with macro_accuracy, per_class_accuracy, confusion_matrix
        """
        self.logger.info("Evaluating on validation set...")

        # Scale features
        X_val_scaled = self.scaler.transform(X_val)

        # Predict
        y_pred = self.classifier.predict(X_val_scaled)

        # Metrics
        macro_accuracy = accuracy_score(y_val, y_pred)
        report = classification_report(y_val, y_pred, output_dict=True, zero_division=0)

        # Per-class accuracy (using precision as proxy)
        per_class = {
            cls: report.get(cls, {}).get('precision', 0.0)
            for cls in self.classifier.classes_
        }

        # Confusion matrix
        conf_matrix = confusion_matrix(y_val, y_pred, labels=self.classifier.classes_)

        results = {
            'macro_accuracy': macro_accuracy,
            'per_class_accuracy': per_class,
            'confusion_matrix': conf_matrix,
            'y_pred': y_pred,
            'classification_report': report
        }

        self.logger.info(f"Macro Accuracy: {macro_accuracy:.2%}")
        for cls, acc in per_class.items():
            self.logger.info(f"  {cls} Accuracy: {acc:.2%}")

        return results

    def generate_confusion_matrix(self, y_true, y_pred, output_path: str):
        """Generate confusion matrix heatmap"""
        conf_matrix = confusion_matrix(y_true, y_pred, labels=self.classifier.classes_)

        fig, ax = plt.subplots(figsize=(8, 6))
        im = ax.imshow(conf_matrix, cmap='Blues')

        # Labels
        ax.set_xticks(range(len(self.classifier.classes_)))
        ax.set_yticks(range(len(self.classifier.classes_)))
        ax.set_xticklabels(self.classifier.classes_)
        ax.set_yticklabels(self.classifier.classes_)

        # Annotations
        for i in range(len(self.classifier.classes_)):
            for j in range(len(self.classifier.classes_)):
                text = ax.text(j, i, conf_matrix[i, j],
                             ha="center", va="center", color="black")

        ax.set_xlabel('Predicted')
        ax.set_ylabel('True')
        ax.set_title('Confusion Matrix')
        plt.colorbar(im, ax=ax)

        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        plt.close()

        self.logger.info(f"Saved confusion matrix to {output_path}")

    def generate_feature_importance(self, feature_names: list, output_path: str):
        """Generate feature importance bar chart"""
        # Logistic regression coefficients: [n_classes, n_features]
        coefficients = self.classifier.coef_

        # Average absolute coefficient across classes
        importance = np.abs(coefficients).mean(axis=0)

        # Sort by importance
        sorted_idx = np.argsort(importance)[::-1]
        sorted_features = [feature_names[i] for i in sorted_idx]
        sorted_importance = importance[sorted_idx]

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(sorted_features, sorted_importance)
        ax.set_xlabel('Average Absolute Coefficient')
        ax.set_ylabel('Feature')
        ax.set_title('Feature Importance')
        ax.invert_yaxis()

        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        plt.close()

        self.logger.info(f"Saved feature importance to {output_path}")

    def generate_r_distribution(self, val_df: pd.DataFrame, output_path: str):
        """Generate histogram of parameter-mass ratio per family"""
        fig, ax = plt.subplots(figsize=(10, 6))

        for family in val_df['family'].unique():
            family_df = val_df[val_df['family'] == family]
            ax.hist(family_df['param_mass_ratio'], alpha=0.6, label=family, bins=15)

        ax.set_xlabel('Parameter-Mass Ratio (R)')
        ax.set_ylabel('Frequency')
        ax.set_title('Parameter-Mass Ratio Distribution by Family')
        ax.legend()

        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        plt.close()

        self.logger.info(f"Saved R distribution to {output_path}")

    def get_misclassified_models(self, val_df: pd.DataFrame, y_pred) -> pd.DataFrame:
        """Return DataFrame of misclassified models"""
        val_df = val_df.copy()
        val_df['predicted'] = y_pred
        val_df['correct'] = val_df['family'] == val_df['predicted']

        misclassified = val_df[~val_df['correct']]
        return misclassified[['model_name', 'family', 'predicted']]
