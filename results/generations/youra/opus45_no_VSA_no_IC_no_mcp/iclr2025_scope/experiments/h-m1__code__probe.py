import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score


def fit_probe(train_emb: np.ndarray, train_labels: np.ndarray, C: float = 1.0,
              max_iter: int = 1000, seed: int = 42) -> LogisticRegression:
    """Fit linear probe on frozen embeddings."""
    probe = LogisticRegression(C=C, max_iter=max_iter, random_state=seed, solver="lbfgs")
    probe.fit(train_emb, train_labels)
    return probe


def probe_accuracy(probe: LogisticRegression, test_emb: np.ndarray,
                   test_labels: np.ndarray) -> float:
    """Evaluate probe accuracy."""
    preds = probe.predict(test_emb)
    return accuracy_score(test_labels, preds)
