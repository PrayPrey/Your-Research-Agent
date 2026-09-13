"""H-M3 data preparation: all 6 conditions (A-F) + canonicalization verification."""
import sys
import numpy as np
from pathlib import Path
from typing import Callable

H_M1_CODE = Path(__file__).parent.parent.parent / "h-m1" / "code"
sys.path.insert(0, str(H_M1_CODE))

from data_loader import load_zoo, SPLITS, EXPECTED_DIM  # noqa: E402

LABEL_NAMES = ["test_accuracy", "generalization_gap", "learning_rate"]

# Layer slices (W1=784x64=50176, b1=64, W2=64x10=640, b2=10; total=50890)
W1_SLICE = slice(0, 50176)
B1_SLICE = slice(50176, 50240)
W2_SLICE = slice(50240, 50880)
B2_SLICE = slice(50880, 50890)
CANON_EPS = 1e-8


def load_and_flatten():
    records = load_zoo()
    X = np.stack([r["weights_flat"].float().numpy() for r in records]).astype(np.float32)
    Y = np.array(
        [[r["test_accuracy"], r["generalization_gap"], r["learning_rate"]] for r in records],
        dtype=np.float32,
    )
    print(f"Loaded zoo: X={X.shape}, Y={Y.shape}")
    return X, Y, LABEL_NAMES


def make_splits(X, Y, val_fraction=0.1, test_fraction=0.1, seed=42):
    """Split into train/val/test."""
    rng = np.random.default_rng(seed)
    N = len(X)
    idx = rng.permutation(N)
    n_test = max(1, int(N * test_fraction))
    n_val = max(1, int(N * val_fraction))
    test_idx = idx[:n_test]
    val_idx = idx[n_test:n_test + n_val]
    train_idx = idx[n_test + n_val:]
    return (X[train_idx], Y[train_idx],
            X[val_idx], Y[val_idx],
            X[test_idx], Y[test_idx])


def apply_condition_a(X: np.ndarray) -> np.ndarray:
    return X.copy()


def apply_condition_b(X: np.ndarray) -> np.ndarray:
    """Scaling only: per-layer Frobenius norm normalization."""
    X_c = X.copy()
    norms_W1 = np.linalg.norm(X_c[:, W1_SLICE], axis=1, keepdims=True) + CANON_EPS
    X_c[:, W1_SLICE] /= norms_W1
    X_c[:, B1_SLICE] /= norms_W1
    norms_W2 = np.linalg.norm(X_c[:, W2_SLICE], axis=1, keepdims=True) + CANON_EPS
    X_c[:, W2_SLICE] /= norms_W2
    X_c[:, B2_SLICE] /= norms_W2
    return X_c


def apply_condition_c(X: np.ndarray) -> np.ndarray:
    """Sign-flip only: majority-sign M=2."""
    N = len(X)
    X_c = X.copy()
    W1 = X_c[:, W1_SLICE].reshape(N, 784, 64)
    W2 = X_c[:, W2_SLICE].reshape(N, 64, 10)
    col_sums = W1.sum(axis=1)
    signs = np.sign(col_sums)
    signs[signs == 0] = 1.0
    W1 *= signs[:, np.newaxis, :]
    W2 *= signs[:, :, np.newaxis]
    X_c[:, W1_SLICE] = W1.reshape(N, 50176)
    X_c[:, W2_SLICE] = W2.reshape(N, 640)
    return X_c


def apply_condition_d(X: np.ndarray) -> np.ndarray:
    """Scaling + sign-flip (both canonicalizations)."""
    N = X.shape[0]
    X_c = X.copy()
    W1_flat = X_c[:, W1_SLICE]
    norms_W1 = np.linalg.norm(W1_flat, axis=1, keepdims=True) + CANON_EPS
    X_c[:, W1_SLICE] = W1_flat / norms_W1
    X_c[:, B1_SLICE] = X_c[:, B1_SLICE] / norms_W1
    W2_flat = X_c[:, W2_SLICE]
    norms_W2 = np.linalg.norm(W2_flat, axis=1, keepdims=True) + CANON_EPS
    X_c[:, W2_SLICE] = W2_flat / norms_W2
    X_c[:, B2_SLICE] = X_c[:, B2_SLICE] / norms_W2
    W1 = X_c[:, W1_SLICE].reshape(N, 784, 64)
    W2 = X_c[:, W2_SLICE].reshape(N, 64, 10)
    col_sums = W1.sum(axis=1)
    signs = np.sign(col_sums)
    signs[signs == 0] = 1.0
    W1 *= signs[:, np.newaxis, :]
    W2 *= signs[:, :, np.newaxis]
    X_c[:, W1_SLICE] = W1.reshape(N, 50176)
    X_c[:, W2_SLICE] = W2.reshape(N, 640)
    return X_c


def apply_condition_e(X: np.ndarray, seed: int = 42) -> np.ndarray:
    """Random norm control: same scale as B, random direction."""
    rng = np.random.default_rng(seed)
    X_b = apply_condition_b(X)
    norms = np.linalg.norm(X_b, axis=1, keepdims=True) + CANON_EPS
    rand_dir = rng.standard_normal(X.shape).astype(np.float32)
    rand_norms = np.linalg.norm(rand_dir, axis=1, keepdims=True) + CANON_EPS
    return (rand_dir / rand_norms) * norms


CONDITION_FNS: dict = {
    'A': apply_condition_a,
    'B': apply_condition_b,
    'C': apply_condition_c,
    'D': apply_condition_d,
    'E': apply_condition_e,
    'F': apply_condition_d,  # same preprocessing; no NFT (linear regressor in main)
}


def verify_canonicalization_activated(condition, X_before, X_after):
    indicators = {}
    N = len(X_after)
    if condition == 'A':
        indicators["no_change"] = bool(np.allclose(X_before, X_after))
    if condition in ('B', 'D', 'F'):
        W1_after = X_after[:, W1_SLICE].reshape(N, 784, 64)
        norms = np.linalg.norm(W1_after, axis=(1, 2))
        indicators["norms_unit"] = float(np.abs(norms - 1.0).mean()) < 0.01
    if condition in ('C', 'D', 'F'):
        W1_after = X_after[:, W1_SLICE].reshape(N, 784, 64)
        col_sums = W1_after.sum(axis=1)
        majority_pos = (col_sums > 0).mean()
        indicators["majority_positive"] = float(majority_pos) > 0.95
    if condition == 'E':
        X_b = apply_condition_b(X_before)
        indicators["differs_from_B"] = not np.allclose(X_after, X_b, atol=1e-3)
    all_pass = all(indicators.values()) if indicators else True
    return all_pass, indicators
