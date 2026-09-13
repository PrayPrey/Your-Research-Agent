import pandas as pd
from typing import Dict


class Evaluator:
    """Evaluate agreement and check gate."""

    def __init__(self, threshold: float = 0.80, fail_threshold: float = 0.70):
        self.threshold = threshold
        self.fail_threshold = fail_threshold

    def evaluate_agreement(
        self, annotations_a1: pd.DataFrame, annotations_a2: pd.DataFrame
    ) -> dict:
        """Compute all kappa scores."""
        from h_m1.agreement import AgreementCalculator
        import numpy as np

        calc = AgreementCalculator()

        # Categorical features
        task_type_kappa = calc.calculate_kappa(
            annotations_a1["task_type"].tolist(), annotations_a2["task_type"].tolist()
        )
        modality_kappa = calc.calculate_kappa(
            annotations_a1["modality"].tolist(), annotations_a2["modality"].tolist()
        )

        # Metrics kappa (flatten lists, compare first metric)
        metrics_a1 = [m[0] if isinstance(m, list) else m for m in annotations_a1["metrics"]]
        metrics_a2 = [m[0] if isinstance(m, list) else m for m in annotations_a2["metrics"]]
        metrics_kappa = calc.calculate_kappa(metrics_a1, metrics_a2)

        # ICC for dataset size
        ratings = np.column_stack(
            [annotations_a1["dataset_size"].values, annotations_a2["dataset_size"].values]
        )
        dataset_size_icc = calc.calculate_icc(ratings)

        return {
            "task_type_kappa": task_type_kappa,
            "modality_kappa": modality_kappa,
            "metrics_kappa": metrics_kappa,
            "dataset_size_icc": dataset_size_icc,
        }

    def check_gate(self, kappa_scores: dict) -> str:
        """MUST_WORK gate decision."""
        all_scores = [
            kappa_scores["task_type_kappa"],
            kappa_scores["modality_kappa"],
            kappa_scores["metrics_kappa"],
            kappa_scores["dataset_size_icc"],
        ]

        if all(k >= self.threshold for k in all_scores):
            return "PASS"
        elif any(k < self.fail_threshold for k in all_scores):
            return "FAIL"
        else:
            return "PARTIAL"
