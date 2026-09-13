import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score
from config import RIDGE_ALPHA, SEED, TEST_SPLIT


def train_test_split_indices(n: int, test_frac: float = TEST_SPLIT, seed: int = SEED):
    """Fixed-seed shuffle split. Returns (train_idx, test_idx)."""
    rng = np.random.default_rng(seed)
    indices = np.arange(n)
    rng.shuffle(indices)
    split = int(n * (1 - test_frac))
    return indices[:split], indices[split:]


class WeightToClassAccuracyProbe:
    def __init__(self, alpha: float = RIDGE_ALPHA):
        self.scaler = StandardScaler()
        self.probe = Ridge(alpha=alpha)

    def fit(self, weight_features: np.ndarray, class_accuracies: np.ndarray):
        """weight_features: (N, 25), class_accuracies: (N, 10)"""
        X = self.scaler.fit_transform(weight_features)
        self.probe.fit(X, class_accuracies)

    def predict(self, weight_features: np.ndarray) -> np.ndarray:
        """Returns (N, 10) predicted class accuracies"""
        X = self.scaler.transform(weight_features)
        return self.probe.predict(X)


def evaluate_r2(y_true: np.ndarray, y_pred: np.ndarray):
    """Compute per-class and mean R². y_true, y_pred: (N, 10)."""
    per_class_r2 = [r2_score(y_true[:, c], y_pred[:, c]) for c in range(y_true.shape[1])]
    mean_r2 = float(np.mean(per_class_r2))
    return per_class_r2, mean_r2


def run_gate_comparison(weight_features, class_wise_acc, overall_acc, baseline_pred, train_idx, test_idx):
    """Compare proposed (weight features) vs baseline (stratified).

    Returns dict with baseline_r2_mean, proposed_r2_mean, gate_pass, per-class R².
    """
    baseline_r2_per_class, baseline_r2_mean = evaluate_r2(
        class_wise_acc[test_idx], baseline_pred[test_idx]
    )

    probe = WeightToClassAccuracyProbe()
    probe.fit(weight_features[train_idx], class_wise_acc[train_idx])
    proposed_pred = probe.predict(weight_features[test_idx])
    proposed_r2_per_class, proposed_r2_mean = evaluate_r2(
        class_wise_acc[test_idx], proposed_pred
    )

    gate_pass = proposed_r2_mean > baseline_r2_mean

    return {
        "baseline_r2_mean": baseline_r2_mean,
        "proposed_r2_mean": proposed_r2_mean,
        "baseline_r2_per_class": baseline_r2_per_class,
        "proposed_r2_per_class": proposed_r2_per_class,
        "gate_pass": gate_pass,
        "proposed_pred": proposed_pred,
    }
