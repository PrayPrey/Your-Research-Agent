"""Compute taxonomy coverage metrics."""

from typing import List, Dict
import json
from ..data_structures import Mapping, CoverageMetrics


class CoverageComputer:
    """Compute taxonomy coverage metrics."""

    def __init__(self, mappings: List[Mapping], threshold: float = 80.0):
        self.mappings = mappings
        self.threshold = threshold

    def compute_aggregate_coverage(self) -> float:
        """Total mapped categories / total categories × 100%."""
        total_categories = len(self.mappings)
        mapped_categories = sum(
            1 for m in self.mappings if m.semantic_primitive is not None
        )

        if total_categories == 0:
            return 0.0

        return (mapped_categories / total_categories) * 100.0

    def compute_per_verifier_coverage(self) -> Dict[str, float]:
        """Coverage for each verifier individually."""
        verifier_stats = {}

        for mapping in self.mappings:
            verifier = mapping.verifier
            if verifier not in verifier_stats:
                verifier_stats[verifier] = {"total": 0, "mapped": 0}

            verifier_stats[verifier]["total"] += 1
            if mapping.semantic_primitive is not None:
                verifier_stats[verifier]["mapped"] += 1

        coverage = {}
        for verifier, stats in verifier_stats.items():
            if stats["total"] > 0:
                coverage[verifier] = (stats["mapped"] / stats["total"]) * 100.0
            else:
                coverage[verifier] = 0.0

        return coverage

    def identify_unmapped_categories(self) -> Dict[str, List[str]]:
        """List categories with no primitive mapping."""
        unmapped = {}

        for mapping in self.mappings:
            if mapping.semantic_primitive is None:
                verifier = mapping.verifier
                if verifier not in unmapped:
                    unmapped[verifier] = []
                unmapped[verifier].append(mapping.error_category)

        return unmapped

    def compute_primitive_frequencies(self) -> Dict[str, int]:
        """Count how many categories map to each primitive."""
        frequencies = {}

        for mapping in self.mappings:
            if mapping.semantic_primitive is not None:
                prim = mapping.semantic_primitive
                frequencies[prim] = frequencies.get(prim, 0) + 1

        return frequencies

    def validate_gate_threshold(self, aggregate_coverage: float, per_verifier_coverage: Dict[str, float]) -> bool:
        """Check if aggregate ≥ threshold AND all verifiers ≥ threshold."""
        aggregate_passed = aggregate_coverage >= self.threshold

        per_verifier_passed = all(
            coverage >= self.threshold
            for coverage in per_verifier_coverage.values()
        )

        return aggregate_passed and per_verifier_passed

    def compute_metrics(self) -> CoverageMetrics:
        """Compute all coverage metrics."""
        aggregate_coverage = self.compute_aggregate_coverage()
        per_verifier_coverage = self.compute_per_verifier_coverage()
        unmapped_categories = self.identify_unmapped_categories()
        primitive_frequencies = self.compute_primitive_frequencies()
        gate_passed = self.validate_gate_threshold(aggregate_coverage, per_verifier_coverage)

        return CoverageMetrics(
            aggregate_coverage=aggregate_coverage,
            per_verifier_coverage=per_verifier_coverage,
            unmapped_categories=unmapped_categories,
            primitive_frequencies=primitive_frequencies,
            gate_passed=gate_passed,
            threshold=self.threshold
        )

    def export_report(self, metrics: CoverageMetrics, output_path: str) -> None:
        """Save coverage report to JSON file."""
        with open(output_path, 'w') as f:
            json.dump(metrics.to_dict(), f, indent=2)
