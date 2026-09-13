"""
Linear Attribution Methods for H-M1 convex experiment.
Implements TRAK, TracIn, IF, FastIF for feature-space logistic regression.
"""

import os
import numpy as np
from typing import Dict, List, Any

from config import HM1Config


# Budget map for convex linear model (consistent with h-e1)
BUDGET_MAP_CONVEX: Dict[str, Dict[int, Any]] = {
    'TRAK':   {10: {'proj_dim': 10},  25: {'proj_dim': 25},  50: {'proj_dim': 50},
               75: {'proj_dim': 75},  100: {'proj_dim': 100}},
    'TracIn': {10: {'n_ckpts': 1},    25: {'n_ckpts': 2},    50: {'n_ckpts': 3},
               75: {'n_ckpts': 4},    100: {'n_ckpts': 5}},
    'IF':     {10: {'depth': 10},     25: {'depth': 25},     50: {'depth': 50},
               75: {'depth': 75},     100: {'depth': 100}},
    'FastIF': {10: {'n_ckpts': 1},    25: {'n_ckpts': 2},    50: {'n_ckpts': 3},
               75: {'n_ckpts': 4},    100: {'n_ckpts': 5}},
}


class LinearAttributionRunner:
    """Run attribution methods on feature-space logistic regression."""

    def __init__(self, cfg: HM1Config, theta: np.ndarray):
        """
        Args:
            cfg: HM1Config configuration
            theta: (D, C) weight matrix from ConvexLogisticModel
        """
        self.cfg = cfg
        self.theta = theta  # (D, C)

    def _softmax(self, logits: np.ndarray) -> np.ndarray:
        """Numerically stable softmax."""
        exp_logits = np.exp(logits - np.max(logits, axis=1, keepdims=True))
        return exp_logits / np.sum(exp_logits, axis=1, keepdims=True)

    def _compute_gradients(
        self, X: np.ndarray, y: np.ndarray
    ) -> np.ndarray:
        """
        Compute per-sample gradients for cross-entropy loss.
        grad_i = x_i * (p_i[y_i] - 1) for the correct class.
        Returns: (N, D)
        """
        N = X.shape[0]
        logits = X @ self.theta  # (N, C)
        probs = self._softmax(logits)  # (N, C)
        correct_probs = probs[np.arange(N), y]  # (N,)
        grad_scale = correct_probs - 1.0  # (N,)
        grads = X * grad_scale[:, np.newaxis]  # (N, D)
        return grads

    def compute_trak_scores(
        self,
        X_train: np.ndarray, y_train: np.ndarray,
        X_test: np.ndarray, y_test: np.ndarray,
        proj_dim: int, seed: int
    ) -> np.ndarray:
        """
        TRAK: Random projection of gradients.
        Returns: (N_train, N_test)
        """
        np.random.seed(seed)

        # Compute gradients
        grad_train = self._compute_gradients(X_train, y_train)  # (N_train, D)
        grad_test = self._compute_gradients(X_test, y_test)    # (N_test, D)

        D = grad_train.shape[1]

        # Random projection matrix
        proj_matrix = np.random.randn(D, proj_dim)
        proj_matrix = proj_matrix / np.linalg.norm(proj_matrix, axis=0, keepdims=True)

        # Project gradients
        train_proj = grad_train @ proj_matrix  # (N_train, proj_dim)
        test_proj = grad_test @ proj_matrix     # (N_test, proj_dim)

        # Dot product scores
        scores = train_proj @ test_proj.T  # (N_train, N_test)
        return scores

    def compute_tracin_scores(
        self,
        X_train: np.ndarray, y_train: np.ndarray,
        X_test: np.ndarray, y_test: np.ndarray,
        n_ckpts: int, seed: int
    ) -> np.ndarray:
        """
        TracIn: Gradient dot-product with checkpoint scaling.
        For convex model, we simulate checkpoint effect with scaling.
        Returns: (N_train, N_test)
        """
        np.random.seed(seed)

        grad_train = self._compute_gradients(X_train, y_train)
        grad_test = self._compute_gradients(X_test, y_test)

        # Scale by number of checkpoints (simulates averaging over training trajectory)
        scale = n_ckpts / 5.0
        scores = scale * (grad_train @ grad_test.T)
        return scores

    def compute_if_scores(
        self,
        X_train: np.ndarray, y_train: np.ndarray,
        X_test: np.ndarray, y_test: np.ndarray,
        depth: int, seed: int,
        H_inv: np.ndarray = None
    ) -> np.ndarray:
        """
        IF: Influence functions with Hessian inverse.
        For convex, we use exact H^{-1} (provided) or approximate.
        Returns: (N_train, N_test)
        """
        np.random.seed(seed)

        grad_train = self._compute_gradients(X_train, y_train)
        grad_test = self._compute_gradients(X_test, y_test)

        if H_inv is not None:
            # Use exact Hessian inverse
            s_test = H_inv @ grad_test.T  # (D, N_test)
            scores = grad_train @ s_test   # (N_train, N_test)
        else:
            # Approximate: simple gradient dot-product scaled by depth
            scale = 1.0 / (depth + 1)
            scores = scale * (grad_train @ grad_test.T)

        return scores

    def compute_fastif_scores(
        self,
        X_train: np.ndarray, y_train: np.ndarray,
        X_test: np.ndarray, y_test: np.ndarray,
        n_ckpts: int, seed: int
    ) -> np.ndarray:
        """
        FastIF: Last-layer gradient similarity.
        For linear model, equivalent to TracIn with different scaling.
        Returns: (N_train, N_test)
        """
        np.random.seed(seed)

        grad_train = self._compute_gradients(X_train, y_train)
        grad_test = self._compute_gradients(X_test, y_test)

        scale = n_ckpts / 5.0
        scores = scale * (grad_train @ grad_test.T)
        return scores

    def compute_method_scores(
        self,
        method_name: str,
        X_train: np.ndarray, y_train: np.ndarray,
        X_test: np.ndarray, y_test: np.ndarray,
        budget: int, seed: int,
        H_inv: np.ndarray = None
    ) -> np.ndarray:
        """
        Compute attribution scores for a given method.
        Returns: (N_train, N_test)
        """
        params = BUDGET_MAP_CONVEX[method_name][budget]

        if method_name == 'TRAK':
            return self.compute_trak_scores(
                X_train, y_train, X_test, y_test,
                proj_dim=params['proj_dim'], seed=seed
            )
        elif method_name == 'TracIn':
            return self.compute_tracin_scores(
                X_train, y_train, X_test, y_test,
                n_ckpts=params['n_ckpts'], seed=seed
            )
        elif method_name == 'IF':
            return self.compute_if_scores(
                X_train, y_train, X_test, y_test,
                depth=params['depth'], seed=seed, H_inv=H_inv
            )
        elif method_name == 'FastIF':
            return self.compute_fastif_scores(
                X_train, y_train, X_test, y_test,
                n_ckpts=params['n_ckpts'], seed=seed
            )
        else:
            raise ValueError(f"Unknown method: {method_name}")

    def run_all(
        self,
        X_train: np.ndarray, y_train: np.ndarray,
        X_test: np.ndarray, y_test: np.ndarray,
        H_inv: np.ndarray = None
    ) -> Dict[str, Dict[int, List[np.ndarray]]]:
        """
        Full grid: 4 methods x 5 budgets x 3 seeds.
        Returns: results[method][budget] = List[np.ndarray(N_train, N_test)]
        """
        results = {method: {} for method in self.cfg.methods}
        total_runs = len(self.cfg.methods) * len(self.cfg.compute_budgets) * len(self.cfg.seeds)
        run_count = 0

        for method in self.cfg.methods:
            for budget in self.cfg.compute_budgets:
                results[method][budget] = []
                for seed in self.cfg.seeds:
                    run_count += 1
                    print(f"  [{run_count}/{total_runs}] {method} budget={budget} seed={seed}")

                    scores = self.compute_method_scores(
                        method, X_train, y_train, X_test, y_test,
                        budget, seed, H_inv=H_inv
                    )
                    results[method][budget].append(scores)

        return results
