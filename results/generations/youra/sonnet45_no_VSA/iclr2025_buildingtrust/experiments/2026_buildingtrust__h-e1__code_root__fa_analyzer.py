"""Factor analysis implementation for H-E1."""

import numpy as np
from sklearn.decomposition import FactorAnalysis, PCA
from typing import Tuple
import warnings


class CrossBenchmarkFactorAnalyzer:
    """Factor analysis with Kaiser criterion and varimax rotation."""

    def __init__(self, random_state: int = 42):
        """
        Initialize factor analyzer.

        Args:
            random_state: Random seed for reproducibility
        """
        self.random_state = random_state
        self.fa_model = None
        self.pca_model = None
        self.eigenvalues = None
        self.n_factors = None
        self.loadings = None
        self.scores = None

    def determine_n_factors(self, X: np.ndarray) -> int:
        """
        Determine number of factors via Kaiser criterion (eigenvalue > 1.0).

        Args:
            X: [N, M] standardized benchmark matrix

        Returns:
            int: Number of factors to retain
        """
        print("\n[Factor Analyzer] Determining number of factors (Kaiser criterion)...")

        # Fit PCA to get eigenvalues
        self.pca_model = PCA(random_state=self.random_state)
        self.pca_model.fit(X)

        # Eigenvalues from explained variance
        self.eigenvalues = self.pca_model.explained_variance_

        # Kaiser criterion: retain factors with eigenvalue > 1.0
        self.n_factors = int(np.sum(self.eigenvalues > 1.0))

        print(f"[Factor Analyzer] Eigenvalues: {self.eigenvalues}")
        print(f"[Factor Analyzer] Number of factors (eigenvalue > 1.0): {self.n_factors}")

        if self.n_factors < 2:
            warnings.warn(f"Only {self.n_factors} factor(s) with eigenvalue >1, expected 2-3")
        elif self.n_factors > 3:
            warnings.warn(f"{self.n_factors} factors with eigenvalue >1, expected 2-3")

        return self.n_factors

    def fit(self, X: np.ndarray, n_factors: int = None) -> FactorAnalysis:
        """
        Fit factor analysis model with varimax rotation.

        Args:
            X: [N, M] standardized benchmark matrix
            n_factors: Number of factors (uses Kaiser if None)

        Returns:
            FactorAnalysis: Fitted model
        """
        if n_factors is None:
            if self.n_factors is None:
                n_factors = self.determine_n_factors(X)
            else:
                n_factors = self.n_factors

        print(f"\n[Factor Analyzer] Fitting Factor Analysis (n_factors={n_factors})...")

        # Fit FA with varimax rotation
        self.fa_model = FactorAnalysis(
            n_components=n_factors,
            rotation='varimax',
            max_iter=1000,
            random_state=self.random_state
        )

        try:
            self.fa_model.fit(X)
            print("[Factor Analyzer] Factor Analysis converged successfully")
        except Exception as e:
            warnings.warn(f"FA convergence issue: {e}, results may be unreliable")

        # Extract loadings
        self.loadings = self.fa_model.components_.T  # [M, n_factors]

        # Compute factor scores
        self.scores = self.fa_model.transform(X)  # [N, n_factors]

        print(f"[Factor Analyzer] Loadings shape: {self.loadings.shape}")
        print(f"[Factor Analyzer] Factor scores shape: {self.scores.shape}")

        return self.fa_model

    def extract_loadings(self) -> np.ndarray:
        """
        Get factor loadings matrix.

        Returns:
            np.ndarray: [M, n_factors] loadings
        """
        if self.loadings is None:
            raise ValueError("Must call fit() before extract_loadings()")
        return self.loadings

    def compute_scores(self, X: np.ndarray = None) -> np.ndarray:
        """
        Compute factor scores for models.

        Args:
            X: Optional [N, M] matrix (uses training data if None)

        Returns:
            np.ndarray: [N, n_factors] factor scores
        """
        if self.fa_model is None:
            raise ValueError("Must call fit() before compute_scores()")

        if X is None:
            return self.scores
        else:
            return self.fa_model.transform(X)

    def explained_variance(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute explained variance from factor loadings.

        Returns:
            Tuple[np.ndarray, np.ndarray]:
                - prop_var: [n_factors] proportion of variance per factor
                - cumulative_var: [n_factors] cumulative variance
        """
        if self.loadings is None:
            raise ValueError("Must call fit() before explained_variance()")

        print("\n[Factor Analyzer] Computing explained variance...")

        # Variance explained by each factor (sum of squared loadings)
        var_exp = np.sum(self.loadings**2, axis=0)

        # Total variance (number of variables for standardized data)
        total_var = self.loadings.shape[0]  # M variables

        # Proportion of variance
        prop_var = var_exp / total_var

        # Cumulative variance
        cumulative_var = np.cumsum(prop_var)

        print(f"[Factor Analyzer] Variance per factor: {prop_var}")
        print(f"[Factor Analyzer] Cumulative variance: {cumulative_var}")
        print(f"[Factor Analyzer] Total explained: {cumulative_var[-1]:.2%}")

        return prop_var, cumulative_var

    def get_summary(self) -> dict:
        """
        Get summary statistics.

        Returns:
            dict: Summary of factor analysis results
        """
        if self.fa_model is None:
            return {"error": "Model not fitted"}

        prop_var, cumulative_var = self.explained_variance()

        return {
            "n_factors": self.n_factors,
            "eigenvalues": self.eigenvalues.tolist() if self.eigenvalues is not None else None,
            "variance_per_factor": prop_var.tolist(),
            "cumulative_variance": cumulative_var.tolist(),
            "total_variance_explained": float(cumulative_var[-1]),
            "loadings_shape": list(self.loadings.shape),
            "scores_shape": list(self.scores.shape)
        }
