"""H-M2 data preparation: load zoo, apply Condition A/D canonicalization."""
import sys
import numpy as np
from pathlib import Path

H_M1_CODE = Path(__file__).parent.parent.parent / "h-m1" / "code"
sys.path.insert(0, str(H_M1_CODE))
from data_loader import load_zoo, SPLITS, EXPECTED_DIM  # noqa: E402

LABEL_NAMES = ["test_accuracy", "generalization_gap", "learning_rate"]


def load_and_flatten() -> tuple:
    """
    Returns:
        X:           np.ndarray (N, 51850) float32  — raw weight vectors
        Y:           np.ndarray (N, 3)     float32  — [test_acc, gen_gap, lr]
        label_names: list[str]
    """
    records = load_zoo()
    X = np.stack([r["weights_flat"].float().numpy() for r in records]).astype(np.float32)
    Y = np.array(
        [[r["test_accuracy"], r["generalization_gap"], r["learning_rate"]] for r in records],
        dtype=np.float32,
    )
    print(f"Loaded zoo: X={X.shape}, Y={Y.shape}")
    return X, Y, LABEL_NAMES


def apply_condition_d(X: np.ndarray) -> np.ndarray:
    """
    Condition D: scaling (per-layer L2 norm) then sign-flip (majority-sign M=2).
    Args:
        X: (N, 51850) raw weight vectors
    Returns:
        X_c: (N, 51850) canonicalized
    """
    # Layer boundaries from SPLITS = [50176, 64, 640, 10]
    # W1: 0:50176, b1: 50176:50240, W2: 50240:50880, b2: 50880:51850
    N = X.shape[0]
    X_c = X.copy()

    # Step 1: Scaling — per-layer Frobenius norm
    # W1 + b1 block: normalize W1 by its norm, apply same norm to b1
    W1_flat = X_c[:, :50176]
    norms_W1 = np.linalg.norm(W1_flat, axis=1, keepdims=True) + 1e-8
    X_c[:, :50176] = W1_flat / norms_W1
    X_c[:, 50176:50240] = X_c[:, 50176:50240] / norms_W1  # b1 same norm

    # W2 + b2 block
    W2_flat = X_c[:, 50240:50880]
    norms_W2 = np.linalg.norm(W2_flat, axis=1, keepdims=True) + 1e-8
    X_c[:, 50240:50880] = W2_flat / norms_W2
    X_c[:, 50880:51850] = X_c[:, 50880:51850] / norms_W2  # b2 same norm

    # Step 2: Sign-flip (M=2) — majority-sign of incoming column → flip W1 col + W2 row
    W1 = X_c[:, :50176].reshape(N, 784, 64)     # (N, 784, 64)
    W2 = X_c[:, 50240:50880].reshape(N, 64, 10)  # (N, 64, 10)

    col_sums = W1.sum(axis=1)   # (N, 64) sum over input dim
    signs = np.sign(col_sums)   # (N, 64)
    signs[signs == 0] = 1.0     # tie-breaking: positive

    W1 *= signs[:, np.newaxis, :]   # (N, 784, 64)
    W2 *= signs[:, :, np.newaxis]   # (N, 64, 10)

    X_c[:, :50176] = W1.reshape(N, 50176)
    X_c[:, 50240:50880] = W2.reshape(N, 640)
    return X_c


def train_test_split_fixed(X: np.ndarray, Y: np.ndarray,
                            test_size: int = 50, seed: int = 42):
    """Fixed train/test split matching H-M1 protocol (450/50, seed=42)."""
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(X))
    test_idx = idx[:test_size]
    train_idx = idx[test_size:]
    return X[train_idx], X[test_idx], Y[train_idx], Y[test_idx]


if __name__ == "__main__":
    X, Y, names = load_and_flatten()
    X_D = apply_condition_d(X)
    assert not np.allclose(X, X_D), "Canonicalization had no effect"
    X_tr, X_te, Y_tr, Y_te = train_test_split_fixed(X, Y)
    print(f"Train: {X_tr.shape}, Test: {X_te.shape}")
    print(f"Mean |X_A - X_D|: {np.mean(np.abs(X - X_D)):.4f}")
    print("data_prep OK")
