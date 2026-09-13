"""
Statistical Testing Module
Permutation test to verify significance vs random baseline
"""

import json
import numpy as np
from typing import Dict, List
from sklearn.metrics import accuracy_score
from sklearn.utils import shuffle


class StatisticalTester:
    """Conduct permutation test"""

    def __init__(self, n_permutations: int = 1000):
        self.n_permutations = n_permutations

    def permutation_test(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        actual_accuracy: float
    ) -> Dict[str, float]:
        """
        Permutation test vs random baseline.
        Returns: {"p_value": float, "permuted_mean": float, "permuted_std": float}
        """
        print(f"🔬 Running permutation test ({self.n_permutations} iterations)...")

        permuted_accuracies = []

        for i in range(self.n_permutations):
            # Shuffle labels
            y_true_shuffled = shuffle(y_true, random_state=i)

            # Compute accuracy with shuffled labels
            perm_acc = accuracy_score(y_true_shuffled, y_pred)
            permuted_accuracies.append(perm_acc)

        # Compute p-value
        p_value = self.compute_p_value(permuted_accuracies, actual_accuracy)

        # Statistics
        permuted_mean = np.mean(permuted_accuracies)
        permuted_std = np.std(permuted_accuracies)

        print(f"  Actual accuracy: {actual_accuracy:.3f}")
        print(f"  Permuted mean: {permuted_mean:.3f} ± {permuted_std:.3f}")
        print(f"  p-value: {p_value:.4f}")

        return {
            "p_value": p_value,
            "actual_accuracy": actual_accuracy,
            "permuted_mean": permuted_mean,
            "permuted_std": permuted_std,
            "permuted_accuracies": permuted_accuracies
        }

    def compute_p_value(self, permuted_accuracies: List[float], actual_accuracy: float) -> float:
        """
        Compute p-value: fraction of permuted >= actual.
        Returns: p_value (0-1)
        """
        permuted_array = np.array(permuted_accuracies)
        p_value = np.mean(permuted_array >= actual_accuracy)
        return p_value

    def save_results(self, results: Dict, filepath: str) -> None:
        """Save to JSON"""
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Remove permuted_accuracies from saved results (too large)
        save_results = {k: v for k, v in results.items() if k != "permuted_accuracies"}

        with open(filepath, 'w') as f:
            json.dump(save_results, f, indent=2)

        print(f"✓ Statistical test results saved to {filepath}")
