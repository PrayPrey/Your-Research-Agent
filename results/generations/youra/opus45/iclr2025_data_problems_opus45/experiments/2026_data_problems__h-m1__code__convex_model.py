"""
Convex Logistic Regression model for H-M1.
Fit sklearn LogisticRegression, compute Hessian, verify positive-definite eigenvalues.
"""

import numpy as np
from scipy.linalg import eigvalsh
from sklearn.linear_model import LogisticRegression
from scipy.special import softmax

from config import HM1Config


class ConvexLogisticModel:
    """Logistic Regression with Hessian verification for convex analysis."""

    def __init__(self, cfg: HM1Config):
        self.cfg = cfg
        self.model = None
        self._theta = None

    def fit(self, X_train: np.ndarray, y_train: np.ndarray) -> 'ConvexLogisticModel':
        """
        Fit sklearn LogisticRegression with L2 regularization.
        C=100 corresponds to lambda=0.01.
        """
        self.model = LogisticRegression(
            C=self.cfg.C,
            solver=self.cfg.lr_solver,
            max_iter=self.cfg.lr_max_iter,
            multi_class='multinomial',
            random_state=self.cfg.subset_seed,
        )
        self.model.fit(X_train, y_train)

        # Cache theta: (D, C) weight matrix
        self._theta = self.model.coef_.T  # sklearn: (C, D) -> transpose to (D, C)

        accuracy = self.model.score(X_train, y_train)
        print(f"Logistic Regression fitted. Training accuracy: {accuracy:.4f}")

        return self

    def get_theta(self) -> np.ndarray:
        """Returns weight matrix (D, C) for Hessian computation."""
        if self._theta is None:
            self._theta = self.model.coef_.T
        return self._theta

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Softmax probabilities. Returns (N, C)."""
        return self.model.predict_proba(X)

    def compute_hessian(self, X: np.ndarray, lambda_reg: float = None) -> np.ndarray:
        """
        H = (1/N) * X^T @ W @ X + lambda * I
        where W = diag(sum over classes of p_c * (1 - p_c)).

        For multinomial logistic regression, the Hessian for each class c is:
        H_c = X^T @ diag(p_c * (1-p_c)) @ X

        We aggregate across classes for the overall Hessian.
        """
        if lambda_reg is None:
            lambda_reg = 1.0 / self.cfg.C  # lambda = 1/C

        N, D = X.shape
        probs = self.predict_proba(X)  # (N, C)

        # Compute aggregated weight per sample: sum_c p_c(1-p_c)
        # This is the trace of the per-sample Hessian block
        weights = np.sum(probs * (1 - probs), axis=1)  # (N,)

        # H = (1/N) * X^T @ diag(weights) @ X + lambda * I
        weighted_X = X * weights[:, np.newaxis]  # (N, D) * (N, 1) -> (N, D)
        H = (X.T @ weighted_X) / N + lambda_reg * np.eye(D)

        return H

    def verify_convexity(self, X: np.ndarray) -> dict:
        """
        Compute Hessian eigenvalues, assert all > 0.
        Returns: {'min_eigenvalue': float, 'max_eigenvalue': float, 'is_convex': bool, 'eigenvalues': ndarray}
        """
        H = self.compute_hessian(X)
        eigenvalues = eigvalsh(H)  # Sorted ascending

        min_eig = float(eigenvalues[0])
        max_eig = float(eigenvalues[-1])
        is_convex = min_eig > 0

        print(f"Hessian eigenvalue range: [{min_eig:.6f}, {max_eig:.6f}]")
        print(f"Convexity verified: {is_convex}")

        return {
            'min_eigenvalue': min_eig,
            'max_eigenvalue': max_eig,
            'is_convex': is_convex,
            'eigenvalues': eigenvalues,
        }
