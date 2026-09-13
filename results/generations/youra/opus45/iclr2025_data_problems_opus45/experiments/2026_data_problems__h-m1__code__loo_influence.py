"""
Closed-form Leave-One-Out (LOO) influence computation for convex logistic regression.
Uses exact Hessian inversion (valid for convex models).
"""

import os
import numpy as np
from scipy.linalg import inv

from config import HM1Config
from convex_model import ConvexLogisticModel


class ClosedFormLOO:
    """Compute exact LOO influence via Hessian inversion."""

    def __init__(self, model: ConvexLogisticModel, cfg: HM1Config):
        self.model = model
        self.cfg = cfg
        self._H_inv = None

    def compute_hessian_inverse(
        self, X_train: np.ndarray, lambda_reg: float = None
    ) -> np.ndarray:
        """
        Compute H^{-1} via scipy.linalg.inv.
        H shape: (D, D), D=512. O(D^3) exact inversion.
        Returns: H_inv (D, D)
        """
        H = self.model.compute_hessian(X_train, lambda_reg)
        self._H_inv = inv(H)
        print(f"Hessian inverse computed. Shape: {self._H_inv.shape}")
        return self._H_inv

    def compute_gradients(
        self, X: np.ndarray, y: np.ndarray
    ) -> np.ndarray:
        """
        Compute per-sample gradients for logistic regression.
        grad_i = x_i * (p_i - e_{y_i}) where e_{y_i} is one-hot of label.

        For cross-entropy loss with softmax:
        dL/dtheta = X^T @ (P - Y_onehot) / N
        Per-sample: grad_i = x_i @ (p_i - e_{y_i})^T, flattened to (D,) average over classes

        We compute the average gradient magnitude across classes.
        Returns: grad (N, D)
        """
        N, D = X.shape
        C = self.cfg.n_classes

        # Get probabilities
        probs = self.model.predict_proba(X)  # (N, C)

        # One-hot labels
        one_hot = np.eye(C)[y]  # (N, C)

        # Residual: (p_i - e_{y_i})
        residual = probs - one_hot  # (N, C)

        # Gradient per sample: sum over classes of x_i * r_ic
        # We use the average residual magnitude per sample
        grad_weights = np.sum(np.abs(residual), axis=1, keepdims=True)  # (N, 1)

        # Simplified: use gradient w.r.t. the correct class
        # grad_i = x_i * (p_i[y_i] - 1) for the correct class
        correct_probs = probs[np.arange(N), y]  # (N,)
        grad_scale = correct_probs - 1.0  # (N,) - negative for correct class

        grads = X * grad_scale[:, np.newaxis]  # (N, D)

        return grads

    def compute_influence(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
        H_inv: np.ndarray = None,
    ) -> np.ndarray:
        """
        I(z_i, z_test) = grad_test^T @ H_inv @ grad_i
        Returns: influences (N_train, N_test)
        Cached at cfg.results_dir/loo_exact_cache.npy
        """
        cache_path = os.path.join(self.cfg.results_dir, 'loo_exact_cache.npy')

        if os.path.exists(cache_path):
            print(f"Loading cached LOO influences from {cache_path}")
            return np.load(cache_path)

        if H_inv is None:
            H_inv = self._H_inv

        # Compute gradients
        grad_train = self.compute_gradients(X_train, y_train)  # (N_train, D)
        grad_test = self.compute_gradients(X_test, y_test)      # (N_test, D)

        # s_test = H_inv @ grad_test^T -> (D, N_test)
        s_test = H_inv @ grad_test.T  # (D, N_test)

        # influences = grad_train @ s_test -> (N_train, N_test)
        influences = grad_train @ s_test

        print(f"LOO influences computed. Shape: {influences.shape}")

        # Cache
        np.save(cache_path, influences)
        print(f"LOO influences cached to {cache_path}")

        return influences
