"""Cross-Dimensional Correlation Analysis for H-M3"""
from scipy.stats import pearsonr
import numpy as np
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class CrossDimensionalCorrelationAnalyzer:
    """Analyze correlation between dimension performance deltas."""
    
    def __init__(self, dimensions: List[str]):
        """Args: dimensions: ["truthfulness", "fairness", "robustness"]"""
        self.dimensions = dimensions
    
    def compute_deltas(
        self,
        pre_scores: Dict[str, float],
        post_scores: Dict[str, float]
    ) -> Dict[str, float]:
        """Compute performance deltas. Returns: {dimension: delta}"""
        deltas = {}
        for dim in self.dimensions:
            if dim in pre_scores and dim in post_scores:
                deltas[dim] = post_scores[dim] - pre_scores[dim]
        return deltas
    
    def compute_pearson_correlation(
        self,
        deltas1: List[float],
        deltas2: List[float]
    ) -> Tuple[float, float]:
        """Compute Pearson correlation. Returns: (r, p_value)"""
        if len(deltas1) != len(deltas2) or len(deltas1) < 2:
            return (0.0, 1.0)
        r, p = pearsonr(deltas1, deltas2)
        return (r, p)
    
    def compute_all_pairs(
        self,
        deltas_per_seed: Dict[int, Dict[str, float]]
    ) -> Dict[str, Tuple[float, float]]:
        """Compute correlations for all dimension pairs. Returns: {pair: (r, p)}"""
        correlations = {}
        
        # Get dimension pairs
        from itertools import combinations
        for dim1, dim2 in combinations(self.dimensions, 2):
            # Collect deltas across seeds
            deltas1 = [deltas_per_seed[seed][dim1] for seed in sorted(deltas_per_seed.keys()) if dim1 in deltas_per_seed[seed]]
            deltas2 = [deltas_per_seed[seed][dim2] for seed in sorted(deltas_per_seed.keys()) if dim2 in deltas_per_seed[seed]]
            
            r, p = self.compute_pearson_correlation(deltas1, deltas2)
            pair_name = f"{dim1}_vs_{dim2}"
            correlations[pair_name] = (r, p)
            logger.info(f"Correlation {pair_name}: r={r:.4f}, p={p:.4f}")
        
        return correlations

class PermutationTester:
    """Permutation testing for random baseline comparison."""
    
    def __init__(self, n_permutations: int = 1000):
        """Args: n_permutations: 1000 (default)"""
        self.n_permutations = n_permutations
    
    def permutation_test(
        self,
        deltas1: List[float],
        deltas2: List[float]
    ) -> float:
        """Run permutation test. Returns: p_value"""
        if len(deltas1) != len(deltas2) or len(deltas1) < 2:
            return 1.0
        
        # Observed correlation
        r_obs, _ = pearsonr(deltas1, deltas2)
        
        # Generate null distribution
        null_dist = []
        deltas2_array = np.array(deltas2)
        for _ in range(self.n_permutations):
            permuted = np.random.permutation(deltas2_array)
            r_null, _ = pearsonr(deltas1, permuted)
            null_dist.append(r_null)
        
        # Compute p-value
        p_perm = np.mean(np.abs(null_dist) >= np.abs(r_obs))
        logger.info(f"Permutation test: observed r={r_obs:.4f}, p_perm={p_perm:.4f}")
        return p_perm

class LayerWiseCorrelationAnalyzer:
    """Correlate per-layer representation changes with dimension-specific deltas."""
    
    def __init__(self, layers: List[str], dimensions: List[str]):
        """Args: layers: 24 layers, dimensions: 3"""
        self.layers = layers
        self.dimensions = dimensions
    
    def correlate_layer_with_dimensions(
        self,
        rep_changes: Dict[str, float],
        perf_deltas: Dict[str, List[float]]
    ) -> Dict[str, Dict[str, Tuple[float, float]]]:
        """Correlate layer changes with dimension deltas.
        
        Args:
            rep_changes: {layer: change_magnitude} (24 layers)
            perf_deltas: {dimension: [delta_seed1, delta_seed2, delta_seed3]} (3 dimensions)
        
        Returns: {layer: {dimension: (r, p)}}"""
        layer_correlations = {}
        
        for layer_name in self.layers:
            if layer_name not in rep_changes:
                continue
            
            rep_change = rep_changes[layer_name]
            layer_corrs = {}
            
            for dim in self.dimensions:
                if dim not in perf_deltas:
                    continue
                
                # Correlate single layer change with 3 seed deltas
                dim_deltas = perf_deltas[dim]
                rep_changes_expanded = [rep_change] * len(dim_deltas)
                
                if len(dim_deltas) >= 2:
                    r, p = pearsonr(rep_changes_expanded, dim_deltas)
                    layer_corrs[dim] = (r, p)
            
            if layer_corrs:
                layer_correlations[layer_name] = layer_corrs
        
        logger.info(f"Layer-wise correlations computed for {len(layer_correlations)} layers")
        return layer_correlations
    
    def identify_dimension_specific_layers(
        self,
        layer_correlations: Dict[str, Dict[str, Tuple[float, float]]],
        threshold: float = 0.05
    ) -> Dict[str, List[str]]:
        """Identify which layers correlate with which dimensions. Returns: {dimension: [layers]}"""
        dim_layers = {dim: [] for dim in self.dimensions}
        
        for layer_name, layer_corrs in layer_correlations.items():
            for dim, (r, p) in layer_corrs.items():
                if p < threshold and abs(r) > 0.2:  # Significant and meaningful
                    dim_layers[dim].append(layer_name)
        
        for dim, layers in dim_layers.items():
            logger.info(f"Dimension {dim}: {len(layers)} significant layers")
        
        return dim_layers
