"""Affine alignment and transfer evaluation for cross-model probe transfer."""

import numpy as np
from sklearn.metrics import roc_auc_score


class AffineAligner:
    def __init__(self):
        self.W = None
        self.b = None

    def fit(self, source_hidden: np.ndarray, target_hidden: np.ndarray) -> None:
        """Paired samples. source ~= target @ W + b. Least-squares solution."""
        source = source_hidden.astype(np.float32)
        target = target_hidden.astype(np.float32)
        N = target.shape[0]
        X = np.hstack([target, np.ones((N, 1), dtype=np.float32)])
        Wb, *_ = np.linalg.lstsq(X, source, rcond=None)
        self.W = Wb[:-1, :]
        self.b = Wb[-1, :]

    def transform(self, target_hidden: np.ndarray) -> np.ndarray:
        if self.W is None:
            return target_hidden.astype(np.float32)
        target = target_hidden.astype(np.float32)
        return target @ self.W + self.b


class TransferEvaluator:
    def __init__(self, probe):
        self.probe = probe

    def evaluate_direct(self, target_hidden: np.ndarray, labels: np.ndarray) -> float | None:
        """Direct evaluation. Returns None if dimension mismatch."""
        expected_dim = self.probe.clf.n_features_in_
        if target_hidden.shape[1] != expected_dim:
            return None
        proba = self.probe.predict_proba(target_hidden)[:, 1]
        return roc_auc_score(labels, proba)

    def evaluate_aligned(
        self, target_hidden: np.ndarray, labels: np.ndarray, aligner: AffineAligner
    ) -> float:
        """Evaluate after affine alignment to source space."""
        aligned = aligner.transform(target_hidden)
        proba = self.probe.predict_proba(aligned)[:, 1]
        return roc_auc_score(labels, proba)
