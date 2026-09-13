"""Results report generation"""

import pandas as pd
import logging
from datetime import datetime


class ResultsReporter:
    """Generate markdown report from validation results"""

    def __init__(self, results: dict, assumptions: dict, val_df: pd.DataFrame = None):
        self.results = results
        self.assumptions = assumptions
        self.val_df = val_df
        self.logger = logging.getLogger(__name__)

    def generate_markdown_report(self, output_path: str, threshold: float = 0.80):
        """Generate comprehensive markdown report"""
        macro_acc = self.results['macro_accuracy']
        per_class = self.results['per_class_accuracy']
        conf_matrix = self.results['confusion_matrix']

        decision = "PASSED" if macro_acc > threshold else "FAILED"

        report = f"""# H-E1 Validation Results: Statistical Features Sufficiency

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Hypothesis ID:** h-e1
**Status:** {decision}

---

## Summary

**Primary Metric:**
- Validation Accuracy: {macro_acc:.2%}
- Threshold: >{threshold:.0%}
- **Decision:** {decision}

**Secondary Metrics:**
"""

        for cls, acc in per_class.items():
            report += f"- {cls} Accuracy: {acc:.2%}\n"

        report += f"\n**Assumption Validation:**\n"
        for test_name, test_result in self.assumptions.items():
            status = "PASSED" if test_result.get('passed', False) else "FAILED"
            report += f"- {test_result.get('test', test_name)}: {status}\n"

        report += "\n---\n\n## Confusion Matrix\n\n"
        report += self._format_confusion_matrix_table(conf_matrix)

        report += "\n![Confusion Matrix](confusion_matrix.png)\n\n---\n\n"

        report += "## Feature Importance\n\n"
        report += self._format_feature_importance_table()

        report += "\n![Feature Importance](feature_importance.png)\n\n---\n\n"

        if 'misclassified' in self.results and len(self.results['misclassified']) > 0:
            report += "## Failure Cases\n\n"
            report += self._format_failure_cases(self.results['misclassified'])

        report += "\n---\n\n## Assumption Validation Details\n\n"
        for test_name, test_result in self.assumptions.items():
            report += f"**{test_result.get('test', test_name)}:**\n"
            for key, value in test_result.items():
                if key not in ['test', 'passed']:
                    if isinstance(value, float):
                        report += f"- {key}: {value:.4f}\n"
                    else:
                        report += f"- {key}: {value}\n"
            report += "\n"

        report += "---\n\n## Next Steps\n\n"
        if decision == "PASSED":
            report += """- Proceed to H-M1: Normalization Layer Fingerprinting
- Update verification_state.yaml: h-e1.validation.status = COMPLETED
- Begin mechanism hypothesis validation
"""
        else:
            report += f"""- Validation accuracy {macro_acc:.2%} did not meet {threshold:.0%} threshold
- Analyze failure patterns in confusion matrix
- Consider alternative features or classifier
"""

        with open(output_path, 'w') as f:
            f.write(report)

        self.logger.info(f"Saved report to {output_path}")

    def _format_confusion_matrix_table(self, conf_matrix) -> str:
        """Format confusion matrix as markdown table"""
        classes = ['CNN', 'Transformer', 'Hybrid']

        table = "|               | Pred: CNN | Pred: Transformer | Pred: Hybrid |\n"
        table += "|---------------|-----------|-------------------|--------------||\n"

        for i, true_cls in enumerate(classes):
            row = f"| True: {true_cls:12s} |"
            for j in range(len(classes)):
                row += f" {conf_matrix[i, j]:9d} |"
            table += row + "\n"

        return table

    def _format_feature_importance_table(self) -> str:
        """Format feature importance as markdown table"""
        import numpy as np

        coefficients = self.results.get('classifier_coef', np.array([[0, 0, 0, 0, 0]]))
        feature_names = ['bn_count', 'ln_count', 'gn_count', 'no_norm_flag', 'param_mass_ratio']

        importance = np.abs(coefficients).mean(axis=0)
        sorted_idx = np.argsort(importance)[::-1]

        table = "| Feature          | Avg Abs Coefficient | Rank |\n"
        table += "|------------------|---------------------|------|\n"

        for rank, idx in enumerate(sorted_idx, 1):
            table += f"| {feature_names[idx]:16s} | {importance[idx]:19.4f} | {rank:4d} |\n"

        return table

    def _format_failure_cases(self, misclassified_df) -> str:
        """Format misclassified models as markdown table"""
        table = f"**Misclassified Models:** {len(misclassified_df)} / {len(self.val_df) if self.val_df is not None else '?'}\n\n"
        table += "| Model Name | True Label | Predicted Label |\n"
        table += "|------------|------------|-----------------||\n"

        for _, row in misclassified_df.iterrows():
            table += f"| {row['model_name']:40s} | {row['family']:10s} | {row['predicted']:15s} |\n"

        return table
