"""
CKA Similarity Module for H-M2 Hypothesis
Computes Centered Kernel Alignment between pre/post intervention representations
"""

import torch
import numpy as np
from typing import Dict, List, Tuple
from scipy.stats import pearsonr
import logging

logger = logging.getLogger(__name__)


class CKASimilarity:
    """Compute CKA similarity between representations."""

    def __init__(self, device: str = "cuda"):
        """
        Args:
            device: Device for computation (GPU-accelerated)
        """
        self.device = device

    def _center_gram(self, K: torch.Tensor) -> torch.Tensor:
        """Center the Gram matrix."""
        n = K.shape[0]
        H = torch.eye(n, device=K.device) - torch.ones((n, n), device=K.device) / n
        return H @ K @ H

    def _hsic(self, K: torch.Tensor, L: torch.Tensor) -> torch.Tensor:
        """Compute Hilbert-Schmidt Independence Criterion."""
        K_c = self._center_gram(K)
        L_c = self._center_gram(L)
        return torch.trace(K_c @ L_c)

    def compute_cka(self, X: torch.Tensor, Y: torch.Tensor) -> float:
        """
        Compute CKA similarity between two representations.

        Args:
            X: Pre-intervention activations [N, F]
            Y: Post-intervention activations [N, F]

        Returns:
            CKA similarity score (0-1)
        """
        # Move to device
        X = X.to(self.device).float()
        Y = Y.to(self.device).float()

        # Compute Gram matrices
        K = X @ X.T
        L = Y @ Y.T

        # Compute HSIC
        hsic_kl = self._hsic(K, L)
        hsic_kk = self._hsic(K, K)
        hsic_ll = self._hsic(L, L)

        # CKA = HSIC(K,L) / sqrt(HSIC(K,K) * HSIC(L,L))
        cka = hsic_kl / torch.sqrt(hsic_kk * hsic_ll + 1e-10)

        return cka.item()

    def compute_layer_cka(
        self,
        pre_acts: Dict[str, torch.Tensor],
        post_acts: Dict[str, torch.Tensor],
        layer_name: str
    ) -> float:
        """Compute CKA for single layer."""
        # Flatten activations: [N, ...] -> [N, F]
        pre = pre_acts[layer_name].flatten(1)
        post = post_acts[layer_name].flatten(1)

        return self.compute_cka(pre, post)

    def compute_all_layers(
        self,
        pre_acts: Dict[str, torch.Tensor],
        post_acts: Dict[str, torch.Tensor],
        layers: List[str]
    ) -> Dict[str, float]:
        """
        Compute CKA for all layers.

        Returns:
            {layer_name: cka_score}
        """
        cka_scores = {}
        for layer_name in layers:
            if layer_name in pre_acts and layer_name in post_acts:
                cka = self.compute_layer_cka(pre_acts, post_acts, layer_name)
                cka_scores[layer_name] = cka
                logger.debug(f"{layer_name}: CKA = {cka:.4f}")
            else:
                logger.warning(f"Layer {layer_name} missing in activations")

        return cka_scores


class CorrelationAnalyzer:
    """Analyze correlation between representation change and performance."""

    def __init__(self, performance_delta: float = 0.0232):
        """
        Args:
            performance_delta: Performance improvement from h-m1 (+2.32% TruthfulQA)
        """
        self.performance_delta = performance_delta

    def compute_representation_change(self, cka_scores: Dict[str, float]) -> Dict[str, float]:
        """
        Compute change magnitude (1 - CKA).

        Returns:
            {layer: change_magnitude}
        """
        return {layer: 1.0 - cka for layer, cka in cka_scores.items()}

    def aggregate_across_replicates(
        self,
        replicate_cka_scores: List[Dict[str, float]]
    ) -> Dict[str, float]:
        """
        Aggregate CKA scores across replicates.

        Returns:
            {layer: mean_cka}
        """
        if not replicate_cka_scores:
            return {}

        # Get all layer names
        layers = list(replicate_cka_scores[0].keys())

        # Compute mean CKA per layer
        aggregated = {}
        for layer in layers:
            cka_values = [rep[layer] for rep in replicate_cka_scores if layer in rep]
            aggregated[layer] = np.mean(cka_values)

        return aggregated

    def correlate_representation_performance(
        self,
        change_magnitudes: List[float],
        performance_delta: float
    ) -> Dict[str, float]:
        """
        Correlate representation change with performance.

        Returns:
            {
                "correlation": float,
                "p_value": float,
                "significant": bool
            }
        """
        if len(change_magnitudes) < 2:
            return {
                "correlation": 0.0,
                "p_value": 1.0,
                "significant": False
            }

        # All layers compared to same performance delta
        perf_deltas = [performance_delta] * len(change_magnitudes)

        # Compute Pearson correlation
        correlation, p_value = pearsonr(change_magnitudes, perf_deltas)

        return {
            "correlation": float(correlation),
            "p_value": float(p_value),
            "significant": p_value < 0.05
        }


class StatisticalAnalyzer:
    """Statistical analysis for gate evaluation."""

    def __init__(self):
        """Initialize statistical analyzer."""
        pass

    def evaluate_gate(
        self,
        cka_scores: Dict[str, float],
        performance_delta: float = 0.0232
    ) -> Dict:
        """
        Evaluate SHOULD_WORK gate.

        Returns:
            {
                "pass": bool,
                "correlation": float,
                "p_value": float,
                "mean_change": float,
                "layers_changed": int
            }
        """
        # Compute representation change
        changes = [1.0 - cka for cka in cka_scores.values()]
        mean_change = np.mean(changes)

        # Correlation with performance
        corr_analyzer = CorrelationAnalyzer(performance_delta)
        corr_result = corr_analyzer.correlate_representation_performance(
            changes, performance_delta
        )

        # Count layers with changes (CKA < 1.0)
        layers_changed = sum(1 for cka in cka_scores.values() if cka < 1.0)

        # Gate: p < 0.05 AND mean_change > 0
        gate_pass = corr_result["p_value"] < 0.05 and mean_change > 0

        return {
            "pass": gate_pass,
            "correlation": corr_result["correlation"],
            "p_value": corr_result["p_value"],
            "mean_change": float(mean_change),
            "layers_changed": layers_changed,
            "total_layers": len(cka_scores)
        }
