"""Main taxonomy construction pipeline."""

import json
from pathlib import Path
from typing import Dict, List

from .extractors.knowledge_base import get_all_categories
from .clustering.semantic_clusterer import SemanticClusterer
from .mapping.mapping_engine import MappingEngine
from .evaluation.coverage_computer import CoverageComputer
from .evaluation.visualizer import Visualizer
from .data_structures import ErrorCategory, CoverageMetrics


class TaxonomyBuilder:
    """Main pipeline: error extraction → primitives → mapping → coverage."""

    def __init__(self, config: Dict):
        self.config = config
        self.categories = None
        self.primitives = None
        self.mappings = None
        self.metrics = None

    def run_pipeline(self) -> CoverageMetrics:
        """Execute full taxonomy construction pipeline."""
        print("=" * 80)
        print("H-E2 Cross-Verifier Taxonomy Construction Pipeline")
        print("=" * 80)

        # Phase 1: Extract error categories
        print("\n[Phase 1] Extracting error categories from verifier documentation...")
        self.categories = get_all_categories()
        self._export_categories()
        total_categories = sum(len(cats) for cats in self.categories.values())
        print(f"  ✓ Extracted {total_categories} error categories:")
        for verifier, cats in self.categories.items():
            print(f"    - {verifier}: {len(cats)} categories")

        # Phase 2: Identify semantic primitives
        print("\n[Phase 2] Identifying semantic primitives...")
        clusterer = SemanticClusterer(self.config['taxonomy']['primitives'])
        self.primitives = clusterer.cluster_by_proof_obligation(self.categories)
        clusterer.export_taxonomy(
            self.primitives,
            self.config['paths']['output']['semantic_primitives']
        )
        print(f"  ✓ Identified {len(self.primitives)} semantic primitives:")
        for prim in self.primitives:
            print(f"    - {prim.primitive_id}")

        # Phase 3: Construct mappings
        print("\n[Phase 3] Constructing category-to-primitive mappings...")
        mapper = MappingEngine(
            self.primitives,
            self.categories,
            self.config['taxonomy']['confidence_threshold']
        )
        self.mappings = mapper.map_all_categories()
        mapper.export_mappings(self.config['paths']['output']['taxonomy_mapping'])
        print(f"  ✓ Generated {len(self.mappings)} mappings")

        # Phase 4: Compute coverage & validate gate
        print("\n[Phase 4] Computing coverage metrics...")
        coverage_computer = CoverageComputer(
            self.mappings,
            self.config['evaluation']['coverage_target'] * 100
        )
        self.metrics = coverage_computer.compute_metrics()
        coverage_computer.export_report(
            self.metrics,
            self.config['paths']['output']['coverage_report']
        )

        print(f"  ✓ Aggregate coverage: {self.metrics.aggregate_coverage:.1f}%")
        print(f"  ✓ Per-verifier coverage:")
        for verifier, coverage in self.metrics.per_verifier_coverage.items():
            status = "✓" if coverage >= self.config['evaluation']['coverage_target'] * 100 else "✗"
            print(f"    {status} {verifier}: {coverage:.1f}%")

        # Phase 5: Generate visualizations
        print("\n[Phase 5] Generating visualizations...")
        visualizer = Visualizer(
            self.config['paths']['output']['figures_dir'],
            self.config['evaluation']['figure_dpi']
        )

        figures_dir = Path(self.config['paths']['output']['figures_dir'])
        figures_dir.mkdir(exist_ok=True)

        visualizer.plot_verifier_coverage_bars(
            self.metrics.per_verifier_coverage,
            self.config['evaluation']['coverage_target'] * 100,
            str(figures_dir / "coverage_bars.png")
        )
        visualizer.plot_primitive_frequencies(
            self.metrics.primitive_frequencies,
            str(figures_dir / "primitive_frequencies.png")
        )
        visualizer.plot_mapping_heatmap(
            self.mappings,
            str(figures_dir / "mapping_heatmap.png")
        )
        visualizer.plot_gate_comparison(
            self.metrics.aggregate_coverage,
            self.metrics.per_verifier_coverage,
            self.config['evaluation']['coverage_target'] * 100,
            str(figures_dir / "gate_comparison.png")
        )
        print(f"  ✓ Generated 4 visualizations in {figures_dir}/")

        # Gate validation
        print("\n" + "=" * 80)
        print("GATE VALIDATION RESULTS")
        print("=" * 80)
        print(f"Threshold: {self.config['evaluation']['coverage_target'] * 100:.0f}%")
        print(f"Aggregate coverage: {self.metrics.aggregate_coverage:.1f}%")
        print(f"Gate status: {'PASSED ✓' if self.metrics.gate_passed else 'FAILED ✗'}")
        print("=" * 80)

        return self.metrics

    def _export_categories(self) -> None:
        """Export error categories to JSON."""
        data = {}
        for verifier, categories in self.categories.items():
            data[verifier] = [cat.to_dict() for cat in categories]

        output_path = self.config['paths']['output']['error_categories']
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
