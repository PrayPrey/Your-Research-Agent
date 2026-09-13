"""Statistics baseline using linear regression on layer-wise weight statistics."""
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error
from typing import List, Tuple, Dict, Any


def extract_layer_stats(state_dict: dict) -> np.ndarray:
    """Extract [mean, std, min, max] per tensor, concatenated."""
    feats = []
    for name, param in state_dict.items():
        t = param.numpy().flatten()
        feats.extend([t.mean(), t.std(), t.min(), t.max()])
    return np.array(feats, dtype=np.float32)


def infer_stats_dim(sample_state_dict: dict) -> int:
    return len(extract_layer_stats(sample_state_dict))


def collate_stats(items: List[Tuple[dict, float]]) -> Tuple[np.ndarray, np.ndarray]:
    """Batch items -> (X [N, D], y [N])."""
    X = np.stack([extract_layer_stats(sd) for sd, _ in items])
    y = np.array([acc for _, acc in items], dtype=np.float32)
    return X, y


class StatisticsBaseline:
    """Linear regression on layer statistics."""
    def __init__(self):
        self.model = LinearRegression()

    def fit(self, X: np.ndarray, y: np.ndarray) -> "StatisticsBaseline":
        self.model.fit(X, y)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)


def train_stats_model(train_items: List[Tuple[dict, float]]) -> StatisticsBaseline:
    """Train statistics baseline on items."""
    X, y = collate_stats(train_items)
    model = StatisticsBaseline()
    model.fit(X, y)
    return model


def evaluate_stats_model(model: StatisticsBaseline, test_items: List[Tuple[dict, float]]) -> Dict[str, Any]:
    """Evaluate statistics model. Returns dict matching evaluate_model output."""
    X, y_true = collate_stats(test_items)
    y_pred = model.predict(X)
    return {
        "r2": r2_score(y_true, y_pred),
        "mae": mean_absolute_error(y_true, y_pred),
        "y_true": y_true,
        "y_pred": y_pred,
    }
