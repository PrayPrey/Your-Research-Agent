"""H-M3 Probes: Linear, Random Baseline, MLP Fallback"""
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import roc_auc_score


class RandomBaseline:
    """Random direction baseline for AUROC floor estimation."""

    def __init__(self, d_model: int = 4096, seed: int = 42):
        self.d_model = d_model
        self.seed = seed
        rng = np.random.default_rng(seed)
        direction = rng.standard_normal(d_model).astype(np.float32)
        self.direction = direction / (np.linalg.norm(direction) + 1e-8)

    def score(self, X: np.ndarray) -> np.ndarray:
        """X @ random_direction."""
        return X @ self.direction


class LinearCorrectnessProbe:
    """Logistic regression probe for correctness prediction."""

    def __init__(self, C: float = 1e-3, max_iter: int = 2000):
        self.clf = LogisticRegression(
            C=C,
            max_iter=max_iter,
            class_weight="balanced",
            solver="lbfgs",
            random_state=42
        )

    def fit(self, X_train: np.ndarray, y_train: np.ndarray) -> "LinearCorrectnessProbe":
        self.clf.fit(X_train, y_train)
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.clf.predict_proba(X)[:, 1]

    def evaluate(self, X_val: np.ndarray, y_val: np.ndarray) -> float:
        probs = self.predict_proba(X_val)
        return roc_auc_score(y_val, probs)


class MLPFallbackProbe:
    """MLP fallback if linear AUROC < 0.70."""

    def __init__(self, hidden_layer_sizes: tuple = (256,), max_iter: int = 500):
        self.clf = MLPClassifier(
            hidden_layer_sizes=hidden_layer_sizes,
            max_iter=max_iter,
            early_stopping=True,
            random_state=42
        )

    def fit(self, X_train: np.ndarray, y_train: np.ndarray) -> "MLPFallbackProbe":
        self.clf.fit(X_train, y_train)
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.clf.predict_proba(X)[:, 1]


def compute_baseline_ci(X_val: np.ndarray, y_val: np.ndarray, d_model: int = 4096, n_seeds: int = 5, base_seed: int = 42) -> dict:
    """Compute random baseline AUROC with confidence interval over multiple seeds."""
    aurocs = []
    for i in range(n_seeds):
        seed = base_seed + i
        rng = np.random.default_rng(seed)
        direction = rng.standard_normal(d_model).astype(np.float32)
        direction /= np.linalg.norm(direction) + 1e-8
        scores = X_val @ direction
        aurocs.append(roc_auc_score(y_val, scores))
    return {"mean": float(np.mean(aurocs)), "std": float(np.std(aurocs)), "values": aurocs}
