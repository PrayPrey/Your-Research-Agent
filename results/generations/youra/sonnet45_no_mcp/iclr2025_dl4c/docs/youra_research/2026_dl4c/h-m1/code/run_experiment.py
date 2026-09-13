#!/usr/bin/env python3
"""H-M1 Benchmark Distinctiveness Analysis - Main Experiment Script"""

import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from data.loader import ExecutionTraceLoader
from analysis.correlation import BenchmarkCorrelationAnalyzer
from analysis.divergence import DistributionDivergenceAnalyzer
from validation.gate_checker import GateConditionEvaluator
from visualization.plots import VisualizationGenerator


class AnalysisPipeline:
    """Main analysis pipeline for h-m1."""

    def __init__(self, h_e1_path: str = "../../h-e1/code/outputs/features.csv"):
        self.h_e1_path = h_e1_path
        self.output_dir = Path("outputs")
        self.figures_dir = Path("figures")
        self.output_dir.mkdir(exist_ok=True)
        self.figures_dir.mkdir(exist_ok=True)
        self.feature_df = None
        self.correlations = {}
        self.divergences = {}
        self.gate_result = {}

    def load_data(self):
        print("="*80)
        print("STEP 1: Loading Data from h-e1")
        print("="*80)
        loader = ExecutionTraceLoader(self.h_e1_path)
        self.feature_df = loader.load_features()
        validation = loader.validate_data_quality()
        print(f"\n✓ Data loaded: {validation['model_count']} models, {validation['benchmark_count']} benchmarks")

    def compute_correlations(self):
        print("\n" + "="*80)
        print("STEP 2: Computing Ranking Correlations")
        print("="*80)
        analyzer = BenchmarkCorrelationAnalyzer(self.feature_df)
        benchmarks = self.feature_df['benchmark'].unique().tolist()
        self.correlations = analyzer.compute_all_pairwise_correlations(benchmarks)
        self.correlation_matrix = analyzer.get_correlation_matrix(benchmarks)
        print(f"\n✓ Correlations computed:")
        for pair, data in self.correlations.items():
            print(f"  {pair}: ρ = {data['rho']:.3f}, p = {data['p_value']:.4f}")

    def compute_divergences(self):
        print("\n" + "="*80)
        print("STEP 3: Computing Distribution Divergences")
        print("="*80)
        analyzer = DistributionDivergenceAnalyzer(self.feature_df)
        benchmarks = self.feature_df['benchmark'].unique().tolist()
        all_divs = analyzer.compute_all_divergences(benchmarks, ['pass@1', 'runtime_q50'])
        self.divergences = analyzer.aggregate_divergence_scores(all_divs)
        print(f"\n✓ Divergences computed:")
        for pair, kl in self.divergences.items():
            print(f"  {pair}: KL = {kl:.4f}")

    def evaluate_gate(self):
        print("\n" + "="*80)
        print("STEP 4: Evaluating Gate Condition")
        print("="*80)
        evaluator = GateConditionEvaluator(self.correlations, self.divergences)
        self.gate_result = evaluator.evaluate_gate()
        print(f"\n✓ Gate: {self.gate_result['gate_satisfied']}")
        for ev in self.gate_result['supporting_evidence']:
            print(f"  • {ev}")

    def generate_visualizations(self):
        print("\n" + "="*80)
        print("STEP 5: Generating Visualizations")
        print("="*80)
        generator = VisualizationGenerator(
            self.correlation_matrix, self.divergences,
            self.feature_df, str(self.figures_dir)
        )
        figures = generator.generate_all_figures()
        print(f"\n✓ Generated {len(figures)} figures")

    def save_results(self):
        print("\n" + "="*80)
        print("STEP 6: Saving Results")
        print("="*80)
        results = {
            'hypothesis_id': 'h-m1',
            'timestamp': datetime.now().isoformat(),
            'correlations': self.correlations,
            'kl_divergence': self.divergences,
            'gate_result': self.gate_result
        }
        with open(self.output_dir / "analysis_results.json", 'w') as f:
            json.dump(results, f, indent=2)
        
        exp_results = {
            'hypothesis_id': 'h-m1',
            'gate_type': 'SHOULD_WORK',
            'gate_satisfied': self.gate_result['gate_satisfied'],
            'metrics': {'correlations': self.correlations, 'kl_divergence': self.divergences},
            'timestamp': datetime.now().isoformat()
        }
        with open(self.output_dir / "experiment_results.json", 'w') as f:
            json.dump(exp_results, f, indent=2)
        print("✓ Results saved")

    def run(self):
        print("\n" + "="*80)
        print("H-M1 BENCHMARK DISTINCTIVENESS ANALYSIS")
        print("="*80)
        try:
            self.load_data()
            self.compute_correlations()
            self.compute_divergences()
            self.evaluate_gate()
            self.generate_visualizations()
            self.save_results()
            print("\n" + "="*80)
            print("ANALYSIS COMPLETE")
            print("="*80)
            print(f"\nGate Result: {'PASS' if self.gate_result['gate_satisfied'] else 'FAIL'}")
            return self.gate_result['gate_satisfied']
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    pipeline = AnalysisPipeline()
    success = pipeline.run()
    sys.exit(0 if success else 1)
