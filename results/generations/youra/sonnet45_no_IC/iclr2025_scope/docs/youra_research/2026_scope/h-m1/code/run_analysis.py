#!/usr/bin/env python3
"""
H-M1 Feature-Ranking Correlation Analysis
Main orchestration script for hypothesis validation.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from data_loader import BenchmarkDataLoader
from feature_computer import Tier1FeatureComputer, Tier2FeatureComputer
from correlation_analyzer import SpearmanCorrelator, CorrelationReporter
from visualizer import CorrelationVisualizer


class AnalysisOrchestrator:
    """Main orchestrator for H-M1 correlation analysis."""

    def __init__(self, config: dict):
        """
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.results = {}

    def run(self):
        """Execute full analysis pipeline."""
        print("=" * 70)
        print("H-M1: Feature-Ranking Correlation Analysis")
        print("=" * 70)
        print(f"Started: {datetime.now().isoformat()}")
        print()

        # Step 1: Load Data
        print("📊 Step 1: Loading benchmark data from H-E1...")
        loader = BenchmarkDataLoader(self.config['data_path'])
        benchmarks = loader.load_benchmarks()
        rankings_df = loader.extract_method_rankings(benchmarks)
        print()

        # Step 2: Compute Features
        print("🔬 Step 2: Computing Tier 1+2 features...")
        tier1_features = Tier1FeatureComputer.compute_features(benchmarks)
        tier2_features = Tier2FeatureComputer.compute_features(benchmarks)

        # Combine features
        features_df = tier1_features.join(tier2_features, how='outer')
        print(f"✓ Total features: {len(features_df.columns)}")
        print(f"  Features: {list(features_df.columns)}")
        print()

        # Save features
        features_path = Path(self.config['output_dir']) / 'features.csv'
        features_df.to_csv(features_path)
        print(f"✓ Features saved: {features_path}")
        print()

        # Step 3: Correlation Analysis
        print("📈 Step 3: Computing Spearman correlations...")
        correlator = SpearmanCorrelator(
            rho_threshold=self.config['rho_threshold'],
            alpha=self.config['alpha']
        )
        correlations = correlator.compute_correlation_matrix(features_df, rankings_df)
        print()

        # Step 4: Generate Report
        print("📋 Step 4: Generating analysis report...")
        reporter = CorrelationReporter(correlations)

        summary_stats = reporter.generate_summary_stats()
        top_correlations = reporter.get_top_correlations(n=5)
        inverse_correlations = reporter.check_inverse_correlations()
        gate_result = reporter.determine_gate_result()

        # Print summary
        print("\n" + "=" * 70)
        print("ANALYSIS RESULTS")
        print("=" * 70)
        print(f"Total pairs analyzed: {summary_stats['total_pairs']}")
        print(f"Significant correlations: {summary_stats['significant_count']}")
        print(f"Mean ρ: {summary_stats['mean_rho']:.3f}")
        print(f"Median p-value: {summary_stats['median_p_value']:.4f}")
        print()

        print("Top 5 Correlations:")
        for i, (name, data) in enumerate(top_correlations, 1):
            sig = "✓" if data['significant'] else "✗"
            print(f"  {i}. {name:<40} ρ={data['rho']:+.3f}, p={data['p_value']:.4f} {sig}")
        print()

        if inverse_correlations:
            print(f"⚠️ Inverse correlations detected: {len(inverse_correlations)}")
            for name, data in inverse_correlations[:3]:
                print(f"  - {name}: ρ={data['rho']:.3f}, p={data['p_value']:.4f}")
        else:
            print("✓ No significant inverse correlations")
        print()

        print("=" * 70)
        print(f"GATE RESULT: {gate_result}")
        print("=" * 70)
        print()

        # Save results
        self._save_results(correlations, summary_stats, gate_result)

        # Step 5: Generate Visualizations
        print("🎨 Step 5: Generating visualizations...")
        visualizer = CorrelationVisualizer(self.config['figures_dir'])
        visualizer.plot_gate_metrics(correlations)
        visualizer.plot_correlation_heatmap(features_df, rankings_df, correlations)
        visualizer.plot_significance(correlations)
        visualizer.plot_top_scatter_plots(features_df, rankings_df, correlations)
        print()

        print("=" * 70)
        print("✅ ANALYSIS COMPLETE")
        print("=" * 70)
        print(f"Completed: {datetime.now().isoformat()}")
        print()

        return gate_result

    def _save_results(self, correlations: dict, summary_stats: dict, gate_result: str):
        """Save analysis results to JSON files."""
        import numpy as np

        output_dir = Path(self.config['output_dir'])
        output_dir.mkdir(parents=True, exist_ok=True)

        # Convert numpy types to Python types for JSON serialization
        def convert_numpy(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert_numpy(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy(item) for item in obj]
            return obj

        # Save correlations
        correlations_path = output_dir / 'correlations.json'
        correlations_clean = convert_numpy(correlations)
        with open(correlations_path, 'w') as f:
            json.dump(correlations_clean, f, indent=2)
        print(f"✓ Correlations saved: {correlations_path}")

        # Save summary
        summary_path = output_dir / 'summary_stats.json'
        summary_data = {
            **convert_numpy(summary_stats),
            'gate_result': gate_result,
            'timestamp': datetime.now().isoformat()
        }
        with open(summary_path, 'w') as f:
            json.dump(summary_data, f, indent=2)
        print(f"✓ Summary saved: {summary_path}")

    def _determine_gate_result(self, significant_count: int) -> str:
        """
        Determine gate result based on significant correlation count.

        Args:
            significant_count: Number of significant correlations

        Returns:
            "PASS", "PARTIAL", or "FAIL"
        """
        if significant_count >= 3:
            return "PASS"
        elif significant_count >= 1:
            return "PARTIAL"
        else:
            return "FAIL"


def main():
    """Main entry point."""
    # Configuration
    config = {
        'data_path': './data/h-e1/benchmarks_collection.jsonl',
        'output_dir': './output',
        'figures_dir': '../figures',
        'rho_threshold': 0.3,
        'alpha': 0.05
    }

    # Run analysis
    orchestrator = AnalysisOrchestrator(config)
    gate_result = orchestrator.run()

    # Exit code based on gate result
    if gate_result == "PASS":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
