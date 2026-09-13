"""Linear fusion of entropy and consistency scores."""
import numpy as np
from sklearn.metrics import roc_auc_score


class LinearFusionScorer:
    """Combine inverse-entropy and consistency via linear weights."""

    def __init__(self, alpha: float = 0.5, beta: float = 0.5):
        self.alpha = alpha
        self.beta = beta

    def normalize(self, values: np.ndarray) -> np.ndarray:
        """Min-max normalize to [0,1]. Returns zeros if range < 1e-8."""
        lo, hi = values.min(), values.max()
        if hi - lo < 1e-8:
            return np.zeros_like(values)
        return (values - lo) / (hi - lo)

    def compute_scores(self, entropy: np.ndarray, consistency: np.ndarray) -> np.ndarray:
        """Compute fused score: alpha*(1-norm_entropy) + beta*norm_consistency."""
        confidence = 1.0 - self.normalize(entropy)  # low entropy -> high confidence
        cons_norm = self.normalize(consistency)
        return self.alpha * confidence + self.beta * cons_norm


def train_test_split_idx(n: int, val_frac: float = 0.1, seed: int = 42) -> tuple:
    """Shuffled index split. Returns (val_idx, test_idx)."""
    rng = np.random.RandomState(seed)
    idx = rng.permutation(n)
    n_val = max(1, int(n * val_frac))
    return idx[:n_val], idx[n_val:]


def grid_search_weights(
    entropy: np.ndarray,
    consistency: np.ndarray,
    labels: np.ndarray,
    alpha_range: list = None,
    beta_range: list = None,
) -> tuple:
    """Grid search alpha,beta on val subset. Returns (best_alpha, best_beta, best_auroc)."""
    if alpha_range is None:
        alpha_range = [round(i * 0.1, 1) for i in range(11)]
    if beta_range is None:
        beta_range = [round(i * 0.1, 1) for i in range(11)]

    best_auroc = -1.0
    best_alpha, best_beta = 0.5, 0.5
    auroc_grid = np.zeros((len(alpha_range), len(beta_range)))

    # Check if we have both classes
    unique_labels = np.unique(labels)
    if len(unique_labels) < 2:
        return best_alpha, best_beta, 0.5, auroc_grid  # can't compute AUROC

    for i, alpha in enumerate(alpha_range):
        for j, beta in enumerate(beta_range):
            scorer = LinearFusionScorer(alpha, beta)
            scores = scorer.compute_scores(entropy, consistency)
            try:
                auroc = roc_auc_score(labels, scores)
            except ValueError:
                auroc = 0.5
            auroc_grid[i, j] = auroc
            if auroc > best_auroc:
                best_auroc = auroc
                best_alpha, best_beta = alpha, beta

    return best_alpha, best_beta, best_auroc, auroc_grid
