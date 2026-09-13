"""Semantic Entropy (SE) baseline implementation."""

import numpy as np
from typing import List
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components


class SemanticEntropy:
    """Hard clustering semantic entropy."""
    
    def __init__(self, epsilon: float):
        self.epsilon = epsilon
    
    def compute(self, S: np.ndarray) -> float:
        """Compute semantic entropy via hard clustering.
        
        Args:
            S: N×N similarity matrix
            
        Returns:
            H_SE entropy value
        """
        N = len(S)
        
        # Construct adjacency matrix
        A = (S >= self.epsilon).astype(int)
        
        # Find connected components (clusters)
        clusters = self._cluster(A)
        
        # Cluster probabilities
        probs = np.array([len(c) / N for c in clusters])
        
        # Shannon entropy
        H = -np.sum(probs * np.log(probs + 1e-10))
        
        return H
    
    def _cluster(self, adj: np.ndarray) -> List[List[int]]:
        """Find connected components via scipy.
        
        Args:
            adj: N×N binary adjacency matrix
            
        Returns:
            List of clusters (each is list of indices)
        """
        N = len(adj)
        
        # Convert to sparse format for efficiency
        adj_sparse = csr_matrix(adj)
        
        # Find connected components
        n_components, labels = connected_components(
            csgraph=adj_sparse,
            directed=False,
            return_labels=True
        )
        
        # Group by component label
        clusters = [[] for _ in range(n_components)]
        for i, label in enumerate(labels):
            clusters[label].append(i)
        
        return clusters
