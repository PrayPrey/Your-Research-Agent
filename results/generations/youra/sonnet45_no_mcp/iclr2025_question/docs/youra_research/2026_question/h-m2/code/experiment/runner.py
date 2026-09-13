"""Experiment orchestration for error signature comparison."""

from typing import Dict, List
import sys
import os
import json


class ExperimentRunner:
    """Orchestrate error signature comparison experiment."""

    def __init__(self, config: Dict):
        """
        Initialize experiment with configuration.

        Args:
            config: Dict with keys: h_m1_code_path, datasets, model_name,
                   k_samples, temperature, significance_threshold, output_dir
        """
        self.config = config
        self.nq_loader = None
        self.tqa_loader = None
        self.generator = None
        self.semantic_estimator = None
        self.consistency_estimator = None
        self.analyzer = None
        self.stats = None
        self.visualizer = None

    def setup_components(self):
        """
        Initialize all pipeline components.

        Sets up:
        - sys.path for h-m1 imports
        - Data loaders (NQ, TQA)
        - Generator from h-m1
        - Uncertainty estimators from h-m1
        - Analyzer, statistics, visualizer
        """
        print("\n" + "="*60)
        print("SETTING UP EXPERIMENT COMPONENTS")
        print("="*60)

        # 1. Import h-m2 modules FIRST (before adding h-m1 to path)
        # Get the h-m2 code directory
        h_m2_code_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if h_m2_code_dir not in sys.path:
            sys.path.insert(0, h_m2_code_dir)

        from data.loader import NQDataLoader, TQADataLoader
        from analysis.signature_analyzer import ErrorSignatureAnalyzer
        from analysis.statistical_tests import StatisticalAnalyzer
        from analysis.visualizer import SignatureVisualizer

        # 2. Add h-m1 code to path
        h_m1_path = os.path.abspath(self.config['h_m1_code_path'])
        if h_m1_path not in sys.path:
            sys.path.insert(0, h_m1_path)
        print(f"Added h-m1 code path: {h_m1_path}")

        # 3. Import h-m1 modules
        from models.generator import MistralGenerator
        from methods.uncertainty import SemanticEntropyEstimator, SelfConsistencyEstimator

        # 4. Initialize data loaders
        print("\nInitializing data loaders...")
        self.nq_loader = NQDataLoader(
            split=self.config['dataset_nq']['split'],
            num_samples=self.config['dataset_nq']['num_samples'],
            seed=self.config['seed']
        )
        self.tqa_loader = TQADataLoader(
            split=self.config['dataset_tqa']['split'],
            num_samples=self.config['dataset_tqa']['num_samples'],
            seed=self.config['seed']
        )

        # 5. Initialize generator from h-m1
        print("\nInitializing Mistral-7B generator...")
        self.generator = MistralGenerator(
            model_name=self.config['model_name'],
            device=self.config['device']
        )
        self.generator.load()

        # 6. Initialize uncertainty estimators from h-m1
        print("\nInitializing uncertainty estimators...")
        self.semantic_estimator = SemanticEntropyEstimator(
            embedding_model=self.config['embedding_model'],
            similarity_threshold=self.config['clustering_threshold']
        )
        self.semantic_estimator.load()

        self.consistency_estimator = SelfConsistencyEstimator()

        # 7. Initialize analyzer
        print("\nInitializing error signature analyzer...")
        self.analyzer = ErrorSignatureAnalyzer(
            semantic_estimator=self.semantic_estimator,
            consistency_estimator=self.consistency_estimator,
            generator=self.generator
        )

        # 8. Initialize statistics and visualizer
        print("\nInitializing statistics and visualizer...")
        self.stats = StatisticalAnalyzer()
        self.visualizer = SignatureVisualizer()

        print("\n" + "="*60)
        print("ALL COMPONENTS READY")
        print("="*60 + "\n")

    def run_experiment(self) -> Dict[str, any]:
        """
        Run full experiment pipeline.

        Returns:
            Dict with keys: 'nq_scores', 'tqa_scores', 'diversity_test',
                           'agreement_test', 'gate_pass', 'figures'
        """
        print("\n" + "="*60)
        print("STARTING EXPERIMENT")
        print("="*60)

        # 1. Setup components
        self.setup_components()

        # 2. Load datasets
        print("\n" + "="*60)
        print("LOADING DATASETS")
        print("="*60)
        nq_questions = self.nq_loader.get_questions()  # 100
        tqa_questions = self.tqa_loader.get_questions()  # 100

        # 3. Analyze both datasets
        print("\n" + "="*60)
        print("ANALYZING DATASETS")
        print("="*60)
        nq_scores = self.analyzer.analyze_dataset(
            nq_questions,
            "NaturalQuestions",
            k=self.config['k_samples'],
            temperature=self.config['temperature']
        )
        tqa_scores = self.analyzer.analyze_dataset(
            tqa_questions,
            "TruthfulQA",
            k=self.config['k_samples'],
            temperature=self.config['temperature']
        )

        # 4. Statistical comparison
        print("\n" + "="*60)
        print("STATISTICAL ANALYSIS")
        print("="*60)
        diversity_test = self.stats.independent_ttest(
            nq_scores['diversity'],
            tqa_scores['diversity']
        )
        agreement_test = self.stats.independent_ttest(
            nq_scores['agreement'],
            tqa_scores['agreement']
        )

        print(f"\nDiversity Comparison:")
        print(f"  NQ mean: {diversity_test['mean1']:.4f} ± {diversity_test['std1']:.4f}")
        print(f"  TQA mean: {diversity_test['mean2']:.4f} ± {diversity_test['std2']:.4f}")
        print(f"  t-statistic: {diversity_test['t_statistic']:.4f}")
        print(f"  p-value: {diversity_test['p_value']:.6f}")

        print(f"\nAgreement Comparison:")
        print(f"  NQ mean: {agreement_test['mean1']:.4f} ± {agreement_test['std1']:.4f}")
        print(f"  TQA mean: {agreement_test['mean2']:.4f} ± {agreement_test['std2']:.4f}")
        print(f"  t-statistic: {agreement_test['t_statistic']:.4f}")
        print(f"  p-value: {agreement_test['p_value']:.6f}")

        # 5. Evaluate gate
        gate_pass = self.stats.evaluate_gate(
            diversity_test,
            threshold=self.config['significance_threshold']
        )

        print("\n" + "="*60)
        print("GATE EVALUATION")
        print("="*60)
        print(f"Gate Type: SHOULD_WORK")
        print(f"Condition: (p < 0.05) AND (NQ diversity > TQA diversity)")
        print(f"Result: {'PASS' if gate_pass else 'FAIL'}")
        print(f"  p-value < 0.05: {diversity_test['p_value'] < 0.05}")
        print(f"  NQ > TQA: {diversity_test['mean1'] > diversity_test['mean2']}")
        print("="*60)

        # 6. Generate visualizations
        self.generate_visualizations(nq_scores, tqa_scores, diversity_test)

        # 7. Save results
        results = {
            'nq_scores': nq_scores,
            'tqa_scores': tqa_scores,
            'diversity_test': diversity_test,
            'agreement_test': agreement_test,
            'gate_pass': gate_pass,
            'comparison': self.analyzer.compare_signatures(nq_scores, tqa_scores)
        }

        # Save to JSON
        os.makedirs(self.config['output_dir'], exist_ok=True)
        results_path = os.path.join(self.config['output_dir'], 'experiment_results.json')
        self.stats.save_results(results, results_path)

        return results

    def generate_visualizations(
        self,
        nq_scores: Dict[str, List[float]],
        tqa_scores: Dict[str, List[float]],
        diversity_test: Dict
    ):
        """Generate all required figures (4 plots)."""
        print("\n" + "="*60)
        print("GENERATING VISUALIZATIONS")
        print("="*60)

        os.makedirs(self.config['figures_dir'], exist_ok=True)

        # 1. Gate metrics comparison
        self.visualizer.plot_gate_comparison(
            nq_div_mean=diversity_test['mean1'],
            tqa_div_mean=diversity_test['mean2'],
            output_path=os.path.join(self.config['figures_dir'], 'gate_metrics_comparison.png')
        )

        # 2. Diversity distribution
        self.visualizer.plot_diversity_distributions(
            nq_scores=nq_scores['diversity'],
            tqa_scores=tqa_scores['diversity'],
            output_path=os.path.join(self.config['figures_dir'], 'diversity_distribution.png')
        )

        # 3. Agreement distribution
        self.visualizer.plot_agreement_distributions(
            nq_scores=nq_scores['agreement'],
            tqa_scores=tqa_scores['agreement'],
            output_path=os.path.join(self.config['figures_dir'], 'agreement_distribution.png')
        )

        # 4. 2D signature space
        self.visualizer.plot_signature_space(
            nq_diversity=nq_scores['diversity'],
            nq_agreement=nq_scores['agreement'],
            tqa_diversity=tqa_scores['diversity'],
            tqa_agreement=tqa_scores['agreement'],
            output_path=os.path.join(self.config['figures_dir'], 'signature_space_2d.png')
        )

        print("\nAll visualizations generated successfully!")
