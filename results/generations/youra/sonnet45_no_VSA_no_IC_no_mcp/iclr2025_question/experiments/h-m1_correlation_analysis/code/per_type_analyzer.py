"""Per-hypothesis-type scaling analysis."""

from typing import Dict, List
from analyzer import CorrelationAnalyzer


class PerTypeAnalyzer:
    """Analyze scaling factors by hypothesis type."""

    def __init__(self, analyzer: CorrelationAnalyzer):
        """Initialize with shared analyzer."""
        self.analyzer = analyzer

    def analyze_types(
        self,
        grouped_corpus: Dict[str, List[Dict]]
    ) -> Dict[str, Dict]:
        """
        Analyze each hypothesis type separately.
        grouped_corpus: {type: [papers]}
        Returns: {type: {"k": float, "r2": float, "n": int}}
        """
        results = {}
        for hyp_type, papers in grouped_corpus.items():
            o10 = [p["overhead_measurements"]["micro_pilot"]["overhead_percent"]
                   for p in papers]
            ofull = [p["overhead_measurements"]["full_scale"]["overhead_percent"]
                     for p in papers]

            k, r2, _ = self.analyzer.fit_linear_regression(o10, ofull)
            results[hyp_type] = {"k": k, "r2": r2, "n": len(papers)}
            print(f"  {hyp_type}: k={k:.3f}, R²={r2:.3f}, n={len(papers)}")

        return results

    def compute_scaling_cv(self, k_by_type: Dict[str, float]) -> float:
        """
        CV of scaling factors across types.
        k_by_type: {type: k}
        """
        k_values = list(k_by_type.values())
        return self.analyzer.compute_cv(k_values)
