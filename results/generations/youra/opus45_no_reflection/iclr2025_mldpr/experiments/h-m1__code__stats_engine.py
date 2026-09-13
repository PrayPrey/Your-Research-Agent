"""Statistical analysis for citation z-scores."""
import numpy as np
from scipy import stats


class StatsEngine:
    def compute_field_stats(self, comparison_papers: list[dict]) -> dict:
        citations = [p["citationCount"] for p in comparison_papers]
        return {
            "mean": float(np.mean(citations)),
            "std": float(np.std(citations)),
            "n": len(citations),
        }

    def compute_zscore(self, citation_count: int, field_mean: float, field_std: float) -> float:
        if field_std == 0:
            return 0.0
        return (citation_count - field_mean) / field_std

    def compute_percentile(self, citation_count: int, field_citations: list[int]) -> float:
        return float(stats.percentileofscore(field_citations, citation_count))

    def evaluate_gate(self, foundation_results: dict, threshold: float = 2.0, min_passing: int = 3) -> bool:
        passing = sum(1 for r in foundation_results.values() if r.get("exceeds_2sigma", False))
        return passing >= min_passing
