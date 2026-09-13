"""Metrics computation module for SVD and entropy analysis."""

from typing import List, Dict
import torch
from torch import Tensor
from scipy.stats import linregress


class MetricsComputer:
    """Compute low-rank and entropy metrics."""

    @staticmethod
    def svd_effective_rank(matrix: Tensor, threshold: float = 0.99) -> float:
        """Compute effective rank via SVD decomposition.

        Args:
            matrix: Attention matrix [B*H, L, L] or [B, H, L, L]
            threshold: Variance explained threshold (default 0.99)

        Returns:
            Average effective rank across samples
        """
        # Ensure shape is [B*H, L, L]
        if matrix.dim() == 4:
            B, H, L, _ = matrix.shape
            matrix = matrix.reshape(B * H, L, L)

        # Convert to float32 for SVD (required on CPU, prevents numerical issues)
        matrix = matrix.float()

        # SVD decomposition
        try:
            U, S, V = torch.linalg.svd(matrix)
        except RuntimeError as e:
            # If on CPU and using Half precision, convert to float
            if matrix.dtype == torch.float16:
                matrix = matrix.float()
                U, S, V = torch.linalg.svd(matrix)
            else:
                raise e

        # Compute variance explained
        variance = S ** 2
        cumsum_variance = torch.cumsum(variance, dim=-1)
        total_variance = cumsum_variance[:, -1:]
        explained_ratio = cumsum_variance / total_variance

        # Find threshold crossing point
        eff_rank = (explained_ratio < threshold).sum(dim=-1) + 1

        return eff_rank.float().mean().item()

    @staticmethod
    def operator_entropy(Q: Tensor, K: Tensor) -> float:
        """Compute operator entropy from Q/K projection matrices.

        Args:
            Q: Query projection matrix [D, D]
            K: Key projection matrix [D, D]

        Returns:
            Operator entropy (proxy via log-spectral norm)
        """
        # Convert to float32 for numerical stability
        Q = Q.float()
        K = K.float()

        # Compute QK product
        QK = torch.matmul(Q, K.T)

        # Use spectral norm (largest singular value) as entropy proxy
        # Deeper layers typically have lower spectral norms (more regularized)
        try:
            U, S, V = torch.linalg.svd(QK)
            # Take log of sum of top singular values
            entropy = torch.log(torch.sum(S[:min(10, len(S))])).item()
        except:
            # Fallback: Frobenius norm
            entropy = torch.log(torch.norm(QK, p='fro')).item()

        return entropy

    @staticmethod
    def entropy_regression(
        layer_indices: List[int], entropies: List[float]
    ) -> Dict[str, float]:
        """Fit linear regression for entropy vs layer depth.

        Args:
            layer_indices: List of layer indices
            entropies: List of entropy values per layer

        Returns:
            Dictionary with slope, intercept, p_value, r_squared
        """
        slope, intercept, r_value, p_value, std_err = linregress(
            layer_indices, entropies
        )

        return {
            "slope": slope,
            "intercept": intercept,
            "p_value": p_value,
            "r_squared": r_value ** 2,
            "std_err": std_err,
        }
