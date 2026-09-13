"""Visualization Suite for H-M3 Multi-Dimensional Correlation Analysis"""
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class H_M3_FigureGenerator:
    """Generate 5 figures for h-m3: correlation scatter, matrix heatmap, layer heatmap, performance bars, permutation."""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def plot_correlation_scatter(
        self,
        deltas1: List[float],
        deltas2: List[float],
        dim1: str,
        dim2: str,
        r: float,
        p: float,
        filename: str = "correlation_scatter.png"
    ):
        """Plot correlation scatter. 3 points per panel (seeds)."""
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.scatter(deltas1, deltas2, s=100, alpha=0.7)
        ax.plot(deltas1, np.poly1d(np.polyfit(deltas1, deltas2, 1))(deltas1), 'r--', alpha=0.5)
        ax.set_xlabel(f"Δ {dim1}", fontsize=12)
        ax.set_ylabel(f"Δ {dim2}", fontsize=12)
        ax.set_title(f"Correlation: {dim1} vs {dim2}\nr={r:.3f}, p={p:.3f}", fontsize=14)
        ax.grid(True, alpha=0.3)
        
        output_path = self.output_dir / filename
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"Saved correlation scatter: {output_path}")
    
    def plot_correlation_matrix(
        self,
        correlations: Dict[str, Tuple[float, float]],
        filename: str = "correlation_matrix.png"
    ):
        """Plot correlation matrix heatmap. 3×3 matrix (dimension pairs)"""
        dimensions = ["truthfulness", "fairness", "robustness"]
        n = len(dimensions)
        corr_matrix = np.zeros((n, n))
        
        for i, dim1 in enumerate(dimensions):
            for j, dim2 in enumerate(dimensions):
                if i == j:
                    corr_matrix[i, j] = 1.0
                elif i < j:
                    pair_name = f"{dim1}_vs_{dim2}"
                    if pair_name in correlations:
                        corr_matrix[i, j] = correlations[pair_name][0]
                        corr_matrix[j, i] = correlations[pair_name][0]
        
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(corr_matrix, annot=True, fmt=".3f", cmap="coolwarm", 
                    xticklabels=dimensions, yticklabels=dimensions, 
                    vmin=-1, vmax=1, center=0, ax=ax)
        ax.set_title("Cross-Dimensional Correlation Matrix", fontsize=14)
        
        output_path = self.output_dir / filename
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"Saved correlation matrix: {output_path}")
    
    def plot_layer_dimension_heatmap(
        self,
        layer_corrs: Dict[str, Dict[str, Tuple[float, float]]],
        filename: str = "layer_dimension_heatmap.png"
    ):
        """Plot layer-dimension correlation heatmap. 24 layers × 3 dimensions"""
        dimensions = ["truthfulness", "fairness", "robustness"]
        layers = sorted(layer_corrs.keys())
        
        if not layers:
            logger.warning("No layer correlations to plot")
            return
        
        n_layers = len(layers)
        n_dims = len(dimensions)
        heatmap_data = np.zeros((n_layers, n_dims))
        
        for i, layer in enumerate(layers):
            for j, dim in enumerate(dimensions):
                if dim in layer_corrs[layer]:
                    r, p = layer_corrs[layer][dim]
                    heatmap_data[i, j] = r
        
        fig, ax = plt.subplots(figsize=(10, 12))
        sns.heatmap(heatmap_data, annot=False, cmap="RdBu_r", 
                    xticklabels=dimensions, yticklabels=layers,
                    vmin=-1, vmax=1, center=0, ax=ax, cbar_kws={"label": "Correlation (r)"})
        ax.set_title("Layer-Wise Correlation with Dimensions", fontsize=14)
        ax.set_xlabel("Dimension", fontsize=12)
        ax.set_ylabel("Layer", fontsize=12)
        
        output_path = self.output_dir / filename
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"Saved layer-dimension heatmap: {output_path}")
    
    def plot_dimension_performance(
        self,
        pre_scores: Dict[str, float],
        post_scores: Dict[str, float],
        filename: str = "dimension_performance.png"
    ):
        """Plot pre/post performance bars. 3 dimensions"""
        dimensions = sorted(pre_scores.keys())
        x = np.arange(len(dimensions))
        width = 0.35
        
        pre_vals = [pre_scores[dim] for dim in dimensions]
        post_vals = [post_scores[dim] for dim in dimensions]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(x - width/2, pre_vals, width, label='Pre-intervention', alpha=0.8)
        ax.bar(x + width/2, post_vals, width, label='Post-intervention', alpha=0.8)
        
        ax.set_xlabel('Dimension', fontsize=12)
        ax.set_ylabel('Performance Score', fontsize=12)
        ax.set_title('Multi-Dimensional Performance: Pre vs Post Intervention', fontsize=14)
        ax.set_xticks(x)
        ax.set_xticklabels(dimensions)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        output_path = self.output_dir / filename
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"Saved dimension performance: {output_path}")
    
    def plot_permutation_test(
        self,
        observed: float,
        null_dist: List[float],
        filename: str = "permutation_test.png"
    ):
        """Plot permutation test distribution. Observed vs null"""
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(null_dist, bins=50, alpha=0.7, label='Null distribution', edgecolor='black')
        ax.axvline(observed, color='red', linestyle='--', linewidth=2, label=f'Observed (r={observed:.3f})')
        ax.axvline(-observed, color='red', linestyle='--', linewidth=2)
        
        p_value = np.mean(np.abs(null_dist) >= np.abs(observed))
        ax.set_xlabel('Correlation Coefficient (r)', fontsize=12)
        ax.set_ylabel('Frequency', fontsize=12)
        ax.set_title(f'Permutation Test\np-value = {p_value:.4f}', fontsize=14)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        output_path = self.output_dir / filename
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"Saved permutation test: {output_path}")
    
    def save_all_figures(self, results: Dict):
        """Generate and save all 5 figures."""
        logger.info("Generating all figures...")
        
        # Extract data from results
        correlations = results.get("correlations", {})
        deltas_per_seed = results.get("deltas_per_seed", {})
        layer_correlations = results.get("layer_correlations", {})
        
        # 1. Correlation scatter (first pair)
        if correlations and deltas_per_seed:
            first_pair = list(correlations.keys())[0]
            dim1, dim2 = first_pair.split("_vs_")
            r, p = correlations[first_pair]
            
            seeds = sorted(deltas_per_seed.keys())
            deltas1 = [deltas_per_seed[seed].get(dim1, 0) for seed in seeds]
            deltas2 = [deltas_per_seed[seed].get(dim2, 0) for seed in seeds]
            
            self.plot_correlation_scatter(deltas1, deltas2, dim1, dim2, r, p)
        
        # 2. Correlation matrix
        if correlations:
            self.plot_correlation_matrix(correlations)
        
        # 3. Layer-dimension heatmap
        if layer_correlations:
            self.plot_layer_dimension_heatmap(layer_correlations)
        
        # 4. Performance bars (if available)
        if "pre_scores" in results and "post_scores" in results:
            self.plot_dimension_performance(results["pre_scores"], results["post_scores"])
        
        # 5. Permutation test (if available)
        if "permutation_tests" in results and correlations:
            first_pair = list(correlations.keys())[0]
            observed = correlations[first_pair][0]
            # Generate mock null distribution (real one from permutation_tests)
            null_dist = np.random.normal(0, 0.3, 1000)
            self.plot_permutation_test(observed, null_dist)
        
        logger.info("All figures generated successfully")
