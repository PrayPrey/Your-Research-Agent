"""
Main Experiment Runner for h-m-integrated
Orchestrates full pipeline: load → encode → cluster → evaluate → visualize
"""

import sys
import json
import numpy as np
from pathlib import Path
from datetime import datetime

# Add code directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config.config import ExperimentConfig
from data.data_loader import DataLoader
from models.embedding_model import EmbeddingModel
from models.clustering_pipeline import ClusteringPipeline
from models.baselines import PermutationBaseline, LDABaseline, LexicalBaseline
from analysis.nmi_evaluator import NMIEvaluator
from analysis.generalization import GeneralizationAnalyzer
from analysis.gate_evaluator import GateEvaluator
from analysis.visualizer import Visualizer


class ExperimentRunner:
    """Main experiment orchestration."""

    def __init__(self, config: ExperimentConfig = None):
        """
        Initialize experiment runner.

        Args:
            config: ExperimentConfig instance (default: create new)
        """
        self.config = config or ExperimentConfig()
        self.results = {}

        print("=" * 80)
        print("H-M-INTEGRATED EXPERIMENT")
        print("=" * 80)
        print(f"Hypothesis: {self.config.hypothesis_statement}")
        print(f"Gate Type: {self.config.gate_type}")
        print(f"Random Seed: {self.config.random_seed}")
        print("=" * 80)

    def run(self):
        """Run full experiment pipeline."""
        # Set random seed
        np.random.seed(self.config.random_seed)

        print("\n" + "=" * 80)
        print("STEP 1: LOAD DATA")
        print("=" * 80)
        data_loader = DataLoader(self.config)
        df = data_loader.load_metadata()
        print(f"Loaded {len(df)} samples")
        print(f"Dataset statistics: {data_loader.get_statistics(df)}")

        # Prepare data
        texts = data_loader.prepare_text_fields(df)
        labels_true = data_loader.get_true_labels(df)
        repositories = data_loader.get_repositories(df)
        scaffolding = data_loader.get_scaffolding(df)

        print(f"Text samples: {len(texts)}")
        print(f"Label distribution: {np.bincount(labels_true)}")

        print("\n" + "=" * 80)
        print("STEP 2: ENCODE TEXTS")
        print("=" * 80)
        embedding_model = EmbeddingModel(self.config)
        embeddings = embedding_model.encode(texts)
        print(f"Embeddings shape: {embeddings.shape}")

        print("\n" + "=" * 80)
        print("STEP 3: SEMANTIC CLUSTERING")
        print("=" * 80)
        clustering = ClusteringPipeline(self.config)
        labels_semantic = clustering.cluster_semantic(embeddings)

        print("\n" + "=" * 80)
        print("STEP 4: BASELINE METHODS")
        print("=" * 80)

        # Permutation baseline
        permutation = PermutationBaseline(self.config)
        labels_permutation = permutation.predict(labels_true)

        # LDA baseline
        lda = LDABaseline(self.config)
        labels_lda = lda.fit_predict(texts)

        # Lexical baseline
        lexical = LexicalBaseline(self.config)
        labels_lexical = lexical.predict(texts)

        print("\n" + "=" * 80)
        print("STEP 5: NMI EVALUATION")
        print("=" * 80)
        nmi_evaluator = NMIEvaluator(self.config)

        predictions = {
            'semantic': labels_semantic,
            'permutation': labels_permutation,
            'lda': labels_lda,
            'lexical': labels_lexical
        }

        nmi_scores = nmi_evaluator.compute_all_nmi(labels_true, predictions)
        baseline_gap = nmi_evaluator.compute_baseline_gap(nmi_scores)

        self.results['nmi_scores'] = nmi_scores
        self.results['baseline_gap'] = baseline_gap

        print("\n" + "=" * 80)
        print("STEP 6: CONTROL EXPERIMENTS")
        print("=" * 80)

        # Length normalization
        texts_normalized = data_loader.apply_length_normalization(texts)
        embeddings_normalized = embedding_model.encode(texts_normalized, show_progress=False)
        labels_normalized = clustering.cluster_semantic(embeddings_normalized)

        # Modality filtering
        texts_filtered = data_loader.apply_modality_filtering(texts)
        embeddings_filtered = embedding_model.encode(texts_filtered, show_progress=False)
        labels_filtered = clustering.cluster_semantic(embeddings_filtered)

        control_results = nmi_evaluator.evaluate_controls(
            labels_true,
            labels_semantic,
            labels_normalized,
            labels_filtered
        )

        self.results['control_results'] = control_results

        print("\n" + "=" * 80)
        print("STEP 7: GENERALIZATION TESTS")
        print("=" * 80)
        gen_analyzer = GeneralizationAnalyzer(self.config)

        # Repository-specific probes
        probe_results = gen_analyzer.train_repository_probes(
            embeddings, labels_true, repositories
        )
        probe_variance = gen_analyzer.compute_probe_variance(probe_results)

        # Repository-specific NMI
        repository_nmis = gen_analyzer.compute_repository_nmi(
            labels_true, labels_semantic, repositories
        )

        # Scaffolding effect
        scaffolding_results = gen_analyzer.analyze_scaffolding_effect(
            labels_true, labels_semantic, scaffolding
        )

        self.results['probe_results'] = probe_results
        self.results['probe_variance'] = probe_variance
        self.results['repository_nmis'] = repository_nmis
        self.results['scaffolding_results'] = scaffolding_results

        print("\n" + "=" * 80)
        print("STEP 8: GATE EVALUATION")
        print("=" * 80)
        gate_evaluator = GateEvaluator(self.config)

        primary = gate_evaluator.evaluate_primary_criteria(nmi_scores, baseline_gap)
        secondary = gate_evaluator.evaluate_secondary_criteria(control_results, probe_variance)
        gate_status = gate_evaluator.determine_gate_status(
            primary, secondary, nmi_scores, baseline_gap
        )
        failure_action = gate_evaluator.generate_failure_action(
            gate_status, nmi_scores, control_results, probe_variance
        )

        self.results['primary_criteria'] = primary
        self.results['secondary_criteria'] = secondary
        self.results['gate_status'] = gate_status
        self.results['failure_action'] = failure_action

        print("\n" + "=" * 80)
        print("STEP 9: VISUALIZATION")
        print("=" * 80)
        visualizer = Visualizer(self.config)

        # Gate metrics (required)
        visualizer.plot_gate_metrics(nmi_scores)

        # Embedding space
        visualizer.plot_embedding_space(embeddings, labels_true, labels_semantic)

        # Confusion matrix
        visualizer.plot_confusion_matrix(labels_true, labels_semantic)

        # Repository stratification
        visualizer.plot_repository_stratification(repository_nmis)

        # Scaffolding effect
        visualizer.plot_scaffolding_effect(scaffolding_results)

        print("\n" + "=" * 80)
        print("STEP 10: SAVE RESULTS")
        print("=" * 80)
        self.save_results()

        print("\n" + "=" * 80)
        print("EXPERIMENT COMPLETE")
        print("=" * 80)
        print(f"Gate Status: {gate_status}")
        print(f"Semantic NMI: {nmi_scores['semantic']:.4f}")
        print(f"Baseline Gap: {baseline_gap:.4f}")
        print(f"Results saved to: {self.config.results_dir}")
        print("=" * 80)

        return self.results

    def save_results(self):
        """Save experiment results to JSON."""
        results_path = Path(self.config.results_dir) / "gate_evaluation.json"

        # Convert numpy types to Python types
        def convert(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert(v) for v in obj]
            return obj

        results_serializable = convert(self.results)
        results_serializable['timestamp'] = datetime.now().isoformat()
        results_serializable['experiment_id'] = self.config.experiment_id

        with open(results_path, 'w') as f:
            json.dump(results_serializable, f, indent=2)

        print(f"Results saved: {results_path}")


def main():
    """Main entry point."""
    config = ExperimentConfig()
    runner = ExperimentRunner(config)
    results = runner.run()
    return results


if __name__ == "__main__":
    main()
