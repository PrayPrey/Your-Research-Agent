import numpy as np
from scipy.stats import spearmanr
from data.loader import ZooData


def compute_split(n: int, seed: int = 42, ratios=(0.8, 0.1, 0.1)):
    rng = np.random.RandomState(seed)
    idx = rng.permutation(n)
    n_train = int(ratios[0] * n)
    n_val = int(ratios[1] * n)
    idx_train = idx[:n_train]
    idx_val = idx[n_train:n_train + n_val]
    idx_test = idx[n_train + n_val:]
    return idx_train, idx_val, idx_test


def run_audit(zoo: ZooData, threshold: float = 0.95) -> float:
    """Compute Spearman(gap, -test_acc). Raise AssertionError if >= threshold."""
    r, p = spearmanr(zoo.gap, -zoo.test_acc)
    print(f"[AUDIT] Spearman(gap, -test_acc) = {r:.4f} (p={p:.2e})")
    print(f"[AUDIT] Gap stats: mean={zoo.gap.mean():.4f} std={zoo.gap.std():.4f} "
          f"min={zoo.gap.min():.4f} max={zoo.gap.max():.4f}")
    if r >= threshold:
        raise AssertionError(
            f"A1 FAIL: gap ≈ -test_acc (r={r:.4f} >= {threshold}); switch to PDFD zoo"
        )
    print(f"[AUDIT] A1 PASS: r={r:.4f} < {threshold}")
    return float(r)
