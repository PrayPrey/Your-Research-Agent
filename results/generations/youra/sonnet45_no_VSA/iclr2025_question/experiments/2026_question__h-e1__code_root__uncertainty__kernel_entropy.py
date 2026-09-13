"""Kernel Language Entropy (KLE) implementation."""

import numpy as np
from typing import Tuple


class KernelEntropy:
    """Gaussian kernel-based language entropy."""
    
    def __init__(self, sigma: float):
        self.sigma = sigma
    
    def compute(self, S: np.ndarray) -> Tuple[float, np.ndarray]:
        """Compute kernel entropy via von Neumann entropy.
        
        Args:
            S: N×N similarity matrix
            
        Returns:
            (H_KLE, eigenvalues)
        """
        # Distance matrix
        D = 1 - S
        
        # Gaussian kernel
        K = np.exp(-D**2 / (2 * self.sigma**2))
        
        # Normalize to density matrix
        K_norm = K / np.trace(K)
        
        # Eigendecomposition
        eigenvalues = np.linalg.eigvalsh(K_norm)

        # Clip small negative eigenvalues (numerical precision issues)
        # Warn if significantly negative
        if eigenvalues.min() < -0.1:
            print(f"Warning: Large negative eigenvalue: {eigenvalues.min()}")

        eigenvalues = np.maximum(eigenvalues, 0)

        # Renormalize after clipping
        if eigenvalues.sum() > 0:
            eigenvalues = eigenvalues / eigenvalues.sum()

        # Von Neumann entropy
        # Filter positive eigenvalues
        pos_eigs = eigenvalues[eigenvalues > 1e-10]
        H = -np.sum(pos_eigs * np.log(pos_eigs))

        return H, eigenvalues
    
    def _kernel(self, S: np.ndarray) -> np.ndarray:
        """Construct Gaussian kernel."""
        D = 1 - S
        return np.exp(-D**2 / (2 * self.sigma**2))
    
    def _validate(self, K: np.ndarray, eigs: np.ndarray) -> bool:
        """Validate kernel is PSD and properly normalized."""
        # Check eigenvalues
        all_positive = np.all(eigs >= -1e-6)
        
        # Check trace
        trace_valid = abs(np.trace(K) - 1.0) < 1e-6
        
        # Check symmetry
        symmetric = np.allclose(K, K.T)
        
        return all_positive and trace_valid and symmetric
