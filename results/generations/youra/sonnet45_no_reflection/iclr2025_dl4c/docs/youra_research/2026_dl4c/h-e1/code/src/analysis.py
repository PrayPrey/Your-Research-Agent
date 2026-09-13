"""
Spectral Analysis Core for H-E1
Eigendecomposition and spectral metrics computation.
"""
import numpy as np
from scipy import stats
from typing import Dict, Tuple, List
import warnings
warnings.filterwarnings('ignore')

class ConfoundRegressor:
    """Remove confounds via linear regression."""

    def fit(self, Y: np.ndarray, X: np.ndarray) -> np.ndarray:
        """
        Remove confound effects via OLS regression.

        Args:
            Y: Outcome matrix [N, 4]
            X: Confound matrix [N, k]

        Returns:
            Y_residual: Residual matrix [N, 4]
        """
        # Add intercept
        X_with_intercept = np.column_stack([np.ones(X.shape[0]), X])

        # Fit OLS for each outcome
        Y_residual = np.zeros_like(Y)
        for j in range(Y.shape[1]):
            beta = np.linalg.lstsq(X_with_intercept, Y[:, j], rcond=None)[0]
            Y_fitted = X_with_intercept @ beta
            Y_residual[:, j] = Y[:, j] - Y_fitted

        return Y_residual

class SpectralAnalyzer:
    """Spectral decomposition and gap computation."""

    def compute_covariance(self, Y_residual: np.ndarray) -> np.ndarray:
        """
        Compute covariance matrix.

        Args:
            Y_residual: Residual matrix [N, 4]

        Returns:
            Sigma: Covariance matrix [4, 4]
        """
        return np.cov(Y_residual, rowvar=False)

    def eigendecomposition(self, Sigma: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Perform eigendecomposition.

        Args:
            Sigma: Covariance matrix [4, 4]

        Returns:
            eigenvalues: Sorted eigenvalues [4] (descending)
            eigenvectors: Eigenvectors [4, 4]
        """
        eigenvalues, eigenvectors = np.linalg.eigh(Sigma)
        # Sort descending
        idx = eigenvalues.argsort()[::-1]
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]

        return eigenvalues, eigenvectors

    def spectral_gap(self, eigenvalues: np.ndarray) -> float:
        """
        Compute spectral gap λ₁/λ₄ (largest to smallest ratio).

        For aspect separability, we want the top eigenvalues (aspect effects)
        to dominate over the smallest (noise).

        Args:
            eigenvalues: Eigenvalues [4] (sorted descending)

        Returns:
            gap: Spectral gap metric (higher = better separability)
        """
        # Gap: ratio of largest to smallest eigenvalue
        lambda_1 = eigenvalues[0]  # Largest (primary aspect effect)
        lambda_4 = eigenvalues[-1]  # Smallest (noise floor)

        # Avoid division by zero
        epsilon = 1e-6
        gap = lambda_1 / (lambda_4 + epsilon)

        return gap

    def cross_aspect_coupling(self, Sigma: np.ndarray) -> float:
        """
        Compute normalized cross-aspect coupling.

        Coupling = mean(|off-diagonal|) / mean(diagonal)
        Lower values indicate better separability.

        Args:
            Sigma: Covariance matrix [4, 4]

        Returns:
            coupling: Mean off-diagonal / mean diagonal (0 = perfect separability)
        """
        # Get diagonal (aspect variances)
        diagonal = np.diag(Sigma)

        # Get off-diagonal elements (cross-aspect covariances)
        # Create mask for off-diagonal elements
        mask = ~np.eye(4, dtype=bool)
        off_diagonal = Sigma[mask]

        # Compute coupling as ratio
        mean_diag = np.mean(diagonal)
        mean_off_diag = np.mean(np.abs(off_diagonal))

        coupling = mean_off_diag / (mean_diag + 1e-6)

        return coupling

class PermutationTest:
    """Permutation test for spectral gap significance."""

    def run(
        self,
        Y_residual: np.ndarray,
        aspect_labels: np.ndarray,
        observed_gap: float,
        n_permutations: int = 1000,
        random_seed: int = 42
    ) -> Dict:
        """
        Run permutation test.

        Args:
            Y_residual: Residual matrix [N, 4]
            aspect_labels: Aspect labels [N]
            observed_gap: Observed spectral gap
            n_permutations: Number of permutations

        Returns:
            result: {null_gaps, p_value, significant}
        """
        np.random.seed(random_seed)

        null_gaps = []
        analyzer = SpectralAnalyzer()

        for _ in range(n_permutations):
            # Shuffle aspect labels
            Y_shuffled = Y_residual.copy()
            np.random.shuffle(Y_shuffled)

            # Recompute spectral gap
            Sigma = analyzer.compute_covariance(Y_shuffled)
            eigenvalues, _ = analyzer.eigendecomposition(Sigma)
            gap = analyzer.spectral_gap(eigenvalues)

            null_gaps.append(gap)

        null_gaps = np.array(null_gaps)

        # Compute p-value
        p_value = np.mean(null_gaps >= observed_gap)

        return {
            'null_gaps': null_gaps,
            'p_value': p_value,
            'significant': p_value < 0.05,
            'null_mean': np.mean(null_gaps),
            'null_std': np.std(null_gaps),
            'percentile_95': np.percentile(null_gaps, 95)
        }

class DirectionalStability:
    """Test directional stability of aspects."""

    def compute_on_axis_projections(
        self,
        Y_residual: np.ndarray,
        aspect_labels: np.ndarray,
        eigenvectors: np.ndarray
    ) -> Dict:
        """
        Compute on-axis projection strength.

        Args:
            Y_residual: Residual matrix [N, 4]
            aspect_labels: Aspect labels [N]
            eigenvectors: Eigenvectors [4, 4]

        Returns:
            result: {z_scores, mean_projection}
        """
        aspects = np.unique(aspect_labels)
        projections = {}

        for i, aspect in enumerate(aspects):
            mask = aspect_labels == aspect
            Y_aspect = Y_residual[mask]

            # Project onto corresponding eigenvector
            proj = Y_aspect @ eigenvectors[:, i]

            projections[aspect] = {
                'mean': np.mean(proj),
                'std': np.std(proj),
                'z_score': np.mean(proj) / (np.std(proj) + 1e-6)
            }

        mean_z_score = np.mean([p['z_score'] for p in projections.values()])

        return {
            'projections': projections,
            'mean_z_score': mean_z_score,
            'significant': mean_z_score > 2.0
        }

class CrossValidator:
    """Leave-one-repository-out cross-validation."""

    def run(
        self,
        Y_residual: np.ndarray,
        repo_ids: np.ndarray
    ) -> Dict:
        """
        LORO cross-validation of eigenspace consistency.

        Args:
            Y_residual: Residual matrix [N, 4]
            repo_ids: Repository IDs [N]

        Returns:
            result: {alignments, mean_alignment}
        """
        unique_repos = np.unique(repo_ids)
        alignments = []

        analyzer = SpectralAnalyzer()

        # Full eigenspace
        Sigma_full = analyzer.compute_covariance(Y_residual)
        _, V_full = analyzer.eigendecomposition(Sigma_full)

        for repo in unique_repos[:10]:  # Limit to 10 for PoC
            # Leave one out
            mask = repo_ids != repo
            Y_loo = Y_residual[mask]

            # Compute LOO eigenspace
            Sigma_loo = analyzer.compute_covariance(Y_loo)
            _, V_loo = analyzer.eigendecomposition(Sigma_loo)

            # Compute subspace alignment (Frobenius norm)
            alignment = np.linalg.norm(V_full.T @ V_loo, 'fro') / 4.0
            alignments.append(alignment)

        return {
            'alignments': alignments,
            'mean_alignment': np.mean(alignments),
            'consistent': np.mean(alignments) >= 0.7
        }

class StatisticalValidator:
    """Integrated statistical validation."""

    def run_full_validation(
        self,
        Y_residual: np.ndarray,
        aspect_labels: np.ndarray,
        repo_ids: np.ndarray
    ) -> Dict:
        """
        Run complete validation pipeline.

        Args:
            Y_residual: Residual matrix [N, 4]
            aspect_labels: Aspect labels [N]
            repo_ids: Repository IDs [N]

        Returns:
            results: Complete validation results
        """
        # Spectral analysis
        analyzer = SpectralAnalyzer()
        Sigma = analyzer.compute_covariance(Y_residual)
        eigenvalues, eigenvectors = analyzer.eigendecomposition(Sigma)
        spectral_gap = analyzer.spectral_gap(eigenvalues)
        coupling = analyzer.cross_aspect_coupling(Sigma)

        # Permutation test
        perm_test = PermutationTest()
        perm_results = perm_test.run(Y_residual, aspect_labels, spectral_gap)

        # Directional stability
        dir_test = DirectionalStability()
        dir_results = dir_test.compute_on_axis_projections(Y_residual, aspect_labels, eigenvectors)

        # Cross-validation
        cv = CrossValidator()
        cv_results = cv.run(Y_residual, repo_ids)

        # Overall pass/fail
        primary_pass = (
            spectral_gap > 2.0 and
            perm_results['significant'] and
            coupling <= 0.2
        )

        secondary_pass = (
            dir_results['significant'] and
            cv_results['consistent']
        )

        return {
            'spectral_analysis': {
                'eigenvalues': eigenvalues.tolist(),
                'spectral_gap': float(spectral_gap),
                'coupling': float(coupling),
                'covariance_matrix': Sigma.tolist()
            },
            'permutation_test': {
                'p_value': float(perm_results['p_value']),
                'significant': bool(perm_results['significant']),
                'null_mean': float(perm_results['null_mean']),
                'null_std': float(perm_results['null_std']),
                'percentile_95': float(perm_results['percentile_95'])
            },
            'directional_stability': {
                'mean_z_score': float(dir_results['mean_z_score']),
                'significant': bool(dir_results['significant'])
            },
            'cross_validation': {
                'mean_alignment': float(cv_results['mean_alignment']),
                'consistent': bool(cv_results['consistent'])
            },
            'gate_evaluation': {
                'primary_criteria_pass': bool(primary_pass),
                'secondary_criteria_pass': bool(secondary_pass),
                'overall_pass': bool(primary_pass and secondary_pass)
            }
        }
