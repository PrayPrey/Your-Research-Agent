import numpy as np
from sklearn.metrics import silhouette_score, accuracy_score
from sklearn.linear_model import LogisticRegression
from typing import Optional


def run_gate_check(probe_acc: float, threshold: float = 0.125) -> bool:
    """Gate check: probe accuracy > random baseline (1/8 = 0.125 for 8 tasks)."""
    return probe_acc > threshold


def per_task_accuracy(probe: LogisticRegression, embeddings: np.ndarray,
                      labels: np.ndarray, task_ids: np.ndarray) -> dict:
    """Compute accuracy per task."""
    preds = probe.predict(embeddings)
    results = {}

    for task_id in np.unique(task_ids):
        mask = task_ids == task_id
        if mask.sum() > 0:
            task_acc = accuracy_score(labels[mask], preds[mask])
            results[int(task_id)] = task_acc

    return results


def silhouette(embeddings: np.ndarray, labels: np.ndarray) -> float:
    """Compute silhouette score for embedding clustering quality."""
    if len(np.unique(labels)) < 2:
        return 0.0
    return silhouette_score(embeddings, labels)
