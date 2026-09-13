from sklearn.metrics import precision_score, recall_score, confusion_matrix
from typing import Dict, Tuple, Any
import pandas as pd
import json


class HealthMetricsEvaluator:
    def __init__(self, metrics_csv: str, ground_truth_json: str):
        self.metrics_df = pd.read_csv(metrics_csv)
        with open(ground_truth_json) as f:
            self.ground_truth = json.load(f)

    def compute_precision_recall(self) -> Tuple[float, float]:
        y_true = [self.ground_truth.get(ds, False) for ds in self.metrics_df['dataset_id']]
        y_pred = self.metrics_df['flagged'].tolist()

        if sum(y_pred) == 0:
            return (0.0, 0.0)

        precision = precision_score(y_true, y_pred, zero_division=0)
        recall = recall_score(y_true, y_pred, zero_division=0)
        return (float(precision), float(recall))

    def compute_confusion_matrix(self) -> Dict[str, int]:
        y_true = [self.ground_truth.get(ds, False) for ds in self.metrics_df['dataset_id']]
        y_pred = self.metrics_df['flagged'].tolist()

        cm = confusion_matrix(y_true, y_pred)
        tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, 0)

        return {
            'tp': int(tp),
            'fp': int(fp),
            'fn': int(fn),
            'tn': int(tn)
        }

    def check_gate_metrics(self) -> Tuple[bool, bool]:
        precision, recall = self.compute_precision_recall()
        precision_pass = precision >= 0.6
        recall_pass = recall >= 0.8
        return (precision_pass, recall_pass)

    def generate_report(self) -> Dict[str, Any]:
        precision, recall = self.compute_precision_recall()
        cm = self.compute_confusion_matrix()
        precision_pass, recall_pass = self.check_gate_metrics()

        gate_status = 'PASS' if (precision_pass and recall_pass) else 'FAIL'

        return {
            'precision': precision,
            'recall': recall,
            'confusion_matrix': cm,
            'precision_pass': precision_pass,
            'recall_pass': recall_pass,
            'gate_status': gate_status
        }
