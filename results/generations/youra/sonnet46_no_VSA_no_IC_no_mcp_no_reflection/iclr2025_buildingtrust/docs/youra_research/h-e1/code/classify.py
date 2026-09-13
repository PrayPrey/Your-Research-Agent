"""FR-4: Classification Pipeline — k-NN LOO + permutation test."""
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import LeaveOneOut, cross_val_score, permutation_test_score


def run_loo_knn(X: np.ndarray, y: np.ndarray, k: int = 1) -> float:
    """LOO cross-validation with k-NN (Euclidean). Returns mean accuracy."""
    clf = KNeighborsClassifier(n_neighbors=k, metric="euclidean")
    loo = LeaveOneOut()
    scores = cross_val_score(clf, X, y, cv=loo, scoring="accuracy")
    return float(scores.mean())


def run_permutation_test(
    X: np.ndarray,
    y: np.ndarray,
    k: int = 1,
    n_permutations: int = 1000,
    random_state: int = 42,
) -> tuple[float, float, np.ndarray]:
    """permutation_test_score with LOO CV.
    Returns: (loo_accuracy, p_value, perm_scores [n_permutations,])
    """
    clf = KNeighborsClassifier(n_neighbors=k, metric="euclidean")
    loo = LeaveOneOut()
    score, perm_scores, p_value = permutation_test_score(
        clf, X, y,
        cv=loo,
        n_permutations=n_permutations,
        scoring="accuracy",
        random_state=random_state,
        n_jobs=-1,
    )
    return float(score), float(p_value), perm_scores


def run_sensitivity(X: np.ndarray, y: np.ndarray) -> dict[int, float]:
    """LOO accuracy for k in {1, 3, 5}."""
    return {k: run_loo_knn(X, y, k=k) for k in [1, 3, 5]}


def main(X: np.ndarray, y: np.ndarray) -> dict:
    """Returns dict with loo_accuracy, p_value, perm_scores, sensitivity."""
    print("Running permutation test (1000 permutations, LOO CV)...")
    loo_accuracy, p_value, perm_scores = run_permutation_test(X, y)

    print("Running sensitivity analysis (k=1,3,5)...")
    sensitivity = run_sensitivity(X, y)

    results = {
        "loo_accuracy": loo_accuracy,
        "p_value": p_value,
        "perm_scores": perm_scores.tolist(),
        "sensitivity": sensitivity,
        "n_models": len(y),
        "n_pairs": len(y) // 2,
        "n_sft": int((y == 0).sum()),
        "n_dpo": int((y == 1).sum()),
    }

    print(f"\n=== Classification Results ===")
    print(f"LOO Accuracy (k=1): {loo_accuracy:.4f}")
    print(f"Permutation p-value: {p_value:.4f}")
    print(f"Sensitivity: k=1→{sensitivity[1]:.3f}, k=3→{sensitivity[3]:.3f}, k=5→{sensitivity[5]:.3f}")

    return results


if __name__ == "__main__":
    # Self-test with synthetic separable data
    rng = np.random.default_rng(42)
    X_sft = rng.normal([0.4, 0.5, 0.6, 0.5], 0.05, (6, 4))
    X_dpo = rng.normal([0.6, 0.7, 0.7, 0.6], 0.05, (6, 4))
    X = np.vstack([X_sft, X_dpo])
    y = np.array([0]*6 + [1]*6)
    results = main(X, y)
    print(f"\nSelf-test: acc={results['loo_accuracy']:.3f}, p={results['p_value']:.4f}")
    assert results["loo_accuracy"] > 0.5, "Self-test failed: classifier should beat chance"
    print("✓ Self-test passed")
