import numpy as np
from typing import Dict, Tuple, List
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score, confusion_matrix


class ClassificationEvaluator:
    def __init__(self):
        """Initialize evaluator."""
        self.predictions = []
        self.true_labels = []
        self.pred_labels = []
        self.scores = []

    def add_prediction(self, true_label: str, pred_label: str, scores: Dict[str, float]) -> None:
        """Store prediction result."""
        self.true_labels.append(true_label)
        self.pred_labels.append(pred_label)
        self.scores.append(scores)
        self.predictions.append({
            "true_label": true_label,
            "pred_label": pred_label,
            "scores": scores
        })

    def compute_metrics(self) -> Dict[str, float]:
        """Compute precision/recall/F1/accuracy. Returns: {precision: float, recall: float, ...}"""
        if len(self.true_labels) == 0:
            return {}

        # Convert to numpy arrays
        label_mapping = {"MAJOR": 0, "MINOR": 1, "PATCH": 2}
        y_true = np.array([label_mapping[label] for label in self.true_labels])
        y_pred = np.array([label_mapping[label] for label in self.pred_labels])

        # Compute overall metrics
        accuracy = accuracy_score(y_true, y_pred)

        # Compute MAJOR-specific metrics (binary: MAJOR vs non-MAJOR)
        y_true_major = (y_true == 0).astype(int)
        y_pred_major = (y_pred == 0).astype(int)

        precision_major = precision_score(y_true_major, y_pred_major, zero_division=0)
        recall_major = recall_score(y_true_major, y_pred_major, zero_division=0)
        f1_major = f1_score(y_true_major, y_pred_major, zero_division=0)

        # Compute macro-averaged metrics
        precision_macro = precision_score(y_true, y_pred, average='macro', zero_division=0)
        recall_macro = recall_score(y_true, y_pred, average='macro', zero_division=0)
        f1_macro = f1_score(y_true, y_pred, average='macro', zero_division=0)

        return {
            "accuracy": accuracy,
            "precision_major": precision_major,
            "recall_major": recall_major,
            "f1_major": f1_major,
            "precision_macro": precision_macro,
            "recall_macro": recall_macro,
            "f1_macro": f1_macro
        }

    def get_confusion_matrix(self) -> np.ndarray:
        """Get 3x3 confusion matrix. Returns: [3, 3]"""
        if len(self.true_labels) == 0:
            return np.zeros((3, 3))

        label_mapping = {"MAJOR": 0, "MINOR": 1, "PATCH": 2}
        y_true = np.array([label_mapping[label] for label in self.true_labels])
        y_pred = np.array([label_mapping[label] for label in self.pred_labels])

        return confusion_matrix(y_true, y_pred, labels=[0, 1, 2])

    def check_gate_condition(self, target_precision: float = 0.70, target_recall: float = 0.85) -> Tuple[bool, Dict]:
        """Check PoC pass: precision>=0.7 AND recall>=0.85. Returns: (passed, metrics)"""
        metrics = self.compute_metrics()

        precision_major = metrics.get("precision_major", 0.0)
        recall_major = metrics.get("recall_major", 0.0)

        passed = precision_major >= target_precision and recall_major >= target_recall

        gate_metrics = {
            "passed": passed,
            "precision_major": precision_major,
            "recall_major": recall_major,
            "target_precision": target_precision,
            "target_recall": target_recall
        }

        return passed, gate_metrics

    def get_per_dataset_results(self, dataset_names: List[str]) -> Dict[str, Dict]:
        """Get per-dataset breakdown of results."""
        results = {}

        for i, name in enumerate(dataset_names):
            if i < len(self.predictions):
                pred = self.predictions[i]
                results[name] = {
                    "true_label": pred["true_label"],
                    "pred_label": pred["pred_label"],
                    "correct": pred["true_label"] == pred["pred_label"],
                    "scores": pred["scores"]
                }

        return results
