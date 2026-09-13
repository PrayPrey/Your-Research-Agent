"""
analyze.py — Statistical analysis for H-M1 attention entropy experiment.

Paired t-test across samples per layer, gate result computation, summary.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Dict, List

import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)


@dataclass
class LayerMetrics:
    layer_idx: int
    baseline_entropy: List[float] = field(default_factory=list)
    proposed_entropy: List[float] = field(default_factory=list)
    baseline_hh_concentration: List[float] = field(default_factory=list)
    proposed_hh_concentration: List[float] = field(default_factory=list)
    n_samples: int = 0


@dataclass
class StatisticalResult:
    layer_idx: int
    entropy_pvalue: float
    entropy_statistic: float
    entropy_mean_diff: float        # proposed - baseline
    hh_pvalue: float
    hh_statistic: float
    hh_mean_diff: float


class MetricsAggregator:
    """Accumulate per-sample per-layer entropy and HH metrics."""

    def __init__(self, num_layers: int):
        self.num_layers = num_layers
        self._layers: Dict[int, LayerMetrics] = {
            i: LayerMetrics(layer_idx=i) for i in range(num_layers)
        }
        self._task_counts: Dict[str, int] = {}
        self._category_counts: Dict[str, int] = {}

    def add_sample(
        self,
        condition: str,
        entropy_per_layer: List[float],
        hh_per_layer: List[float],
        task: str,
        category: str,
    ) -> None:
        """Add one sample's metrics for a given condition."""
        assert condition in ("baseline", "eviction-aware"), (
            f"Unknown condition: {condition}"
        )
        n = min(len(entropy_per_layer), self.num_layers)
        for i in range(n):
            lm = self._layers[i]
            if condition == "baseline":
                lm.baseline_entropy.append(entropy_per_layer[i])
                lm.baseline_hh_concentration.append(hh_per_layer[i])
            else:
                lm.proposed_entropy.append(entropy_per_layer[i])
                lm.proposed_hh_concentration.append(hh_per_layer[i])

        if condition == "baseline":
            # Count samples only once (baseline adds the primary count)
            self._layers[0].n_samples += 1
        self._task_counts[task] = self._task_counts.get(task, 0) + 1
        self._category_counts[category] = self._category_counts.get(category, 0) + 1

    def get_layer_metrics(self) -> List[LayerMetrics]:
        """Return list of LayerMetrics sorted by layer_idx."""
        result = []
        for i in range(self.num_layers):
            lm = self._layers[i]
            lm.n_samples = min(len(lm.baseline_entropy), len(lm.proposed_entropy))
            result.append(lm)
        return result

    def save(self, path: str) -> None:
        """Serialize aggregated metrics to JSON."""
        import os
        os.makedirs(os.path.dirname(path), exist_ok=True)
        data = {
            "num_layers": self.num_layers,
            "task_counts": self._task_counts,
            "category_counts": self._category_counts,
            "layers": [
                {
                    "layer_idx": lm.layer_idx,
                    "baseline_entropy": lm.baseline_entropy,
                    "proposed_entropy": lm.proposed_entropy,
                    "baseline_hh_concentration": lm.baseline_hh_concentration,
                    "proposed_hh_concentration": lm.proposed_hh_concentration,
                    "n_samples": lm.n_samples,
                }
                for lm in self.get_layer_metrics()
            ],
        }
        with open(path, "w") as f:
            json.dump(data, f)
        logger.info(f"MetricsAggregator saved to {path}")

    @classmethod
    def load(cls, path: str) -> "MetricsAggregator":
        """Deserialize from JSON."""
        with open(path) as f:
            data = json.load(f)
        agg = cls(num_layers=data["num_layers"])
        agg._task_counts = data.get("task_counts", {})
        agg._category_counts = data.get("category_counts", {})
        for layer_data in data["layers"]:
            i = layer_data["layer_idx"]
            lm = agg._layers[i]
            lm.baseline_entropy = layer_data["baseline_entropy"]
            lm.proposed_entropy = layer_data["proposed_entropy"]
            lm.baseline_hh_concentration = layer_data["baseline_hh_concentration"]
            lm.proposed_hh_concentration = layer_data["proposed_hh_concentration"]
            lm.n_samples = layer_data["n_samples"]
        return agg


class StatisticalAnalyzer:
    """Paired t-test per layer for entropy and HH concentration."""

    def run_paired_ttest(
        self, layer_metrics: List[LayerMetrics]
    ) -> List[StatisticalResult]:
        """Run paired t-test for each layer."""
        results: List[StatisticalResult] = []
        for lm in layer_metrics:
            n = min(len(lm.baseline_entropy), len(lm.proposed_entropy))
            if n < 2:
                results.append(StatisticalResult(
                    layer_idx=lm.layer_idx,
                    entropy_pvalue=1.0, entropy_statistic=0.0, entropy_mean_diff=0.0,
                    hh_pvalue=1.0, hh_statistic=0.0, hh_mean_diff=0.0,
                ))
                continue

            b_e = np.array(lm.baseline_entropy[:n])
            p_e = np.array(lm.proposed_entropy[:n])
            b_hh = np.array(lm.baseline_hh_concentration[:n])
            p_hh = np.array(lm.proposed_hh_concentration[:n])

            e_stat, e_pval = stats.ttest_rel(p_e, b_e)
            hh_stat, hh_pval = stats.ttest_rel(p_hh, b_hh)

            results.append(StatisticalResult(
                layer_idx=lm.layer_idx,
                entropy_pvalue=float(e_pval),
                entropy_statistic=float(e_stat),
                entropy_mean_diff=float((p_e - b_e).mean()),
                hh_pvalue=float(hh_pval),
                hh_statistic=float(hh_stat),
                hh_mean_diff=float((p_hh - b_hh).mean()),
            ))
        return results

    def compute_gate_result(
        self,
        results: List[StatisticalResult],
        significance_threshold: float = 0.05,
        gate_fraction: float = 0.5,
    ) -> dict:
        """Gate: paired t-test p < threshold on >= gate_fraction of layers.

        Returns: {passed, fraction_significant, significant_layers}
        """
        n_layers = len(results)
        if n_layers == 0:
            return {"passed": False, "fraction_significant": 0.0, "significant_layers": []}

        significant = [
            r.layer_idx for r in results
            if r.entropy_pvalue < significance_threshold
            or r.hh_pvalue < significance_threshold
        ]
        fraction = len(significant) / n_layers
        return {
            "passed": fraction >= gate_fraction,
            "fraction_significant": fraction,
            "significant_layers": significant,
        }

    def summarize(self, results: List[StatisticalResult]) -> dict:
        """Summarize statistical results across layers."""
        if not results:
            return {}
        e_pvals = [r.entropy_pvalue for r in results]
        hh_pvals = [r.hh_pvalue for r in results]
        e_diffs = [r.entropy_mean_diff for r in results]
        hh_diffs = [r.hh_mean_diff for r in results]
        return {
            "num_layers": len(results),
            "entropy_min_pvalue": float(min(e_pvals)),
            "entropy_mean_diff": float(np.mean(e_diffs)),
            "hh_min_pvalue": float(min(hh_pvals)),
            "hh_mean_diff": float(np.mean(hh_diffs)),
            "layers_entropy_significant_005": int(sum(p < 0.05 for p in e_pvals)),
            "layers_hh_significant_005": int(sum(p < 0.05 for p in hh_pvals)),
        }
