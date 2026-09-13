"""
Evaluation Module for Temporal Dataset Cards
Implements all experimental evaluations
"""

import numpy as np
from typing import Dict, List, Tuple
from framework import TemporalDatasetCard, ImpactTracer, RetroAnnotation
from baselines import (
    StaticDocumentationSystem,
    SimpleVersioningSystem,
    ReproducibilityEvaluator,
    AnnotationPropagationEvaluator,
    ImpactTracingEvaluator
)
from dataset_generator import DatasetEvolutionSimulator, PaperSimulator, DeprecationScenarioGenerator


class ExperimentRunner:
    """Main experiment runner for all evaluations"""

    def __init__(self, seed: int = 42):
        self.seed = seed
        np.random.seed(seed)

    def run_experiment_1_reproducibility(self) -> Dict:
        """
        Experiment 1: Reproducibility Improvement
        Compare result variance with and without version tracking
        """
        print("Running Experiment 1: Reproducibility Improvement...")

        # Simulate reproduction attempts with temporal cards
        with_tracking = ReproducibilityEvaluator.simulate_reproduction_experiment(
            has_version_tracking=True,
            num_papers=50,
            seed=self.seed
        )

        # Simulate reproduction attempts without temporal cards
        without_tracking = ReproducibilityEvaluator.simulate_reproduction_experiment(
            has_version_tracking=False,
            num_papers=50,
            seed=self.seed + 1
        )

        # Compute improvement metrics
        improvement = ReproducibilityEvaluator.compute_reproducibility_improvement(
            with_tracking, without_tracking
        )

        return {
            'with_temporal_cards': with_tracking,
            'without_temporal_cards': without_tracking,
            'improvement': improvement
        }

    def run_experiment_2_impact_tracing(self) -> Dict:
        """
        Experiment 2: Impact Tracing Accuracy
        Evaluate automated citation extraction accuracy
        """
        print("Running Experiment 2: Impact Tracing Accuracy...")

        # Automated tracing with temporal cards
        automated = ImpactTracingEvaluator.simulate_impact_tracing(
            uses_automated_tracing=True,
            num_papers=200,
            true_positives_base=150,
            seed=self.seed
        )

        # Manual review baseline
        manual = ImpactTracingEvaluator.simulate_impact_tracing(
            uses_automated_tracing=False,
            num_papers=200,
            true_positives_base=150,
            seed=self.seed + 1
        )

        return {
            'automated_tracing': automated,
            'manual_review': manual
        }

    def run_experiment_3_annotation_propagation(self) -> Dict:
        """
        Experiment 3: Annotation Propagation Effectiveness
        Evaluate speed and coverage of issue propagation
        """
        print("Running Experiment 3: Annotation Propagation Effectiveness...")

        # With temporal card system
        with_system = AnnotationPropagationEvaluator.simulate_annotation_propagation(
            has_temporal_system=True,
            num_versions=10,
            affected_versions=5,
            seed=self.seed
        )

        # Without temporal card system (manual)
        without_system = AnnotationPropagationEvaluator.simulate_annotation_propagation(
            has_temporal_system=False,
            num_versions=10,
            affected_versions=5,
            seed=self.seed + 1
        )

        return {
            'with_temporal_system': with_system,
            'without_temporal_system': without_system
        }

    def run_experiment_4_statistical_signatures(self) -> Dict:
        """
        Experiment 4: Statistical Signature Sensitivity
        Test whether statistical signatures detect meaningful differences
        """
        print("Running Experiment 4: Statistical Signature Sensitivity...")

        # Generate dataset versions
        simulator = DatasetEvolutionSimulator(seed=self.seed)
        versions = simulator.generate_dataset_versions(n_versions=5, base_size=1000)

        # Create temporal card
        card = TemporalDatasetCard("test_dataset")

        # Add all versions and compute signatures
        from framework import VersionMetadata, StatisticalSignature

        version_ids = []
        for version_id, data, labels in versions:
            version_ids.append(version_id)

            signature = card.compute_statistical_signature(data, labels)
            changelog = card.generate_changelog(
                versions[0][1] if version_id != versions[0][0] else [],
                data
            )

            metadata = VersionMetadata(
                version_id=version_id,
                timestamp=f"2024-01-{len(card.versions)+1:02d}",
                authors=["Dataset Curator"],
                description=f"Version {version_id}",
                license="MIT",
                changelog=changelog,
                statistical_signature=signature,
                retrospective_annotations=[]
            )

            card.add_version(metadata)

        # Compute KL divergences between consecutive versions
        divergences = []
        for i in range(len(version_ids) - 1):
            kl_div = card.kl_divergence(version_ids[i], version_ids[i+1])
            js_dist = card.jensen_shannon_distance(version_ids[i], version_ids[i+1])
            divergences.append({
                'from_version': version_ids[i],
                'to_version': version_ids[i+1],
                'kl_divergence': kl_div,
                'js_distance': js_dist
            })

        # Simulate result variance for each version
        paper_sim = PaperSimulator(seed=self.seed)
        papers = paper_sim.generate_papers(n_papers=100, dataset_versions=version_ids)

        # Group results by version
        version_results = {v: [] for v in version_ids}
        for paper in papers:
            version_results[paper['dataset_version']].append(paper['reported_accuracy'])

        # Compute variance metrics
        result_variances = {}
        for version, results in version_results.items():
            if results:
                result_variances[version] = {
                    'mean': float(np.mean(results)),
                    'variance': float(np.var(results)),
                    'std': float(np.std(results))
                }

        return {
            'divergences': divergences,
            'result_variances': result_variances,
            'version_ids': version_ids
        }

    def run_experiment_5_changelog_accuracy(self) -> Dict:
        """
        Experiment 5: Changelog Generation Accuracy
        Evaluate automated changelog generation
        """
        print("Running Experiment 5: Changelog Generation Accuracy...")

        simulator = DatasetEvolutionSimulator(seed=self.seed)

        # Generate two versions
        base_data, base_labels = simulator.generate_base_dataset(n_samples=1000)
        new_data, new_labels = simulator.evolve_dataset_add_samples(
            base_data, base_labels, add_ratio=0.1
        )

        # Generate changelog
        card = TemporalDatasetCard("test_dataset")
        changelog = card.generate_changelog(base_data, new_data)

        # Verify accuracy
        accuracy_metrics = {
            'operations_detected': len(changelog),
            'add_operations': sum(1 for op in changelog if op.operation_type == 'ADD'),
            'delete_operations': sum(1 for op in changelog if op.operation_type == 'DELETE'),
            'expected_additions': len(new_data) - len(base_data),
            'changelog_complete': len(changelog) > 0
        }

        return accuracy_metrics

    def run_all_experiments(self) -> Dict:
        """Run all experiments and return comprehensive results"""
        print("\n" + "="*60)
        print("RUNNING ALL EXPERIMENTS")
        print("="*60 + "\n")

        results = {
            'experiment_1_reproducibility': self.run_experiment_1_reproducibility(),
            'experiment_2_impact_tracing': self.run_experiment_2_impact_tracing(),
            'experiment_3_annotation_propagation': self.run_experiment_3_annotation_propagation(),
            'experiment_4_statistical_signatures': self.run_experiment_4_statistical_signatures(),
            'experiment_5_changelog_accuracy': self.run_experiment_5_changelog_accuracy()
        }

        print("\n" + "="*60)
        print("ALL EXPERIMENTS COMPLETED")
        print("="*60 + "\n")

        return results


def compute_summary_metrics(results: Dict) -> Dict:
    """Compute summary metrics across all experiments"""

    summary = {
        'reproducibility': {
            'variance_reduction': results['experiment_1_reproducibility']['improvement']['variance_reduction_percent'],
            'success_rate_improvement': results['experiment_1_reproducibility']['improvement']['success_rate_improvement_percent']
        },
        'impact_tracing': {
            'automated_f1': results['experiment_2_impact_tracing']['automated_tracing']['f1_score'],
            'manual_f1': results['experiment_2_impact_tracing']['manual_review']['f1_score'],
            'f1_improvement': (
                results['experiment_2_impact_tracing']['automated_tracing']['f1_score'] -
                results['experiment_2_impact_tracing']['manual_review']['f1_score']
            )
        },
        'annotation_propagation': {
            'temporal_system_rate': results['experiment_3_annotation_propagation']['with_temporal_system']['propagation_rate'],
            'manual_rate': results['experiment_3_annotation_propagation']['without_temporal_system']['propagation_rate'],
            'notification_time_reduction': (
                results['experiment_3_annotation_propagation']['without_temporal_system']['avg_notification_time_days'] -
                results['experiment_3_annotation_propagation']['with_temporal_system']['avg_notification_time_days']
            )
        },
        'statistical_signatures': {
            'num_versions_tracked': len(results['experiment_4_statistical_signatures']['version_ids']),
            'num_divergences_computed': len(results['experiment_4_statistical_signatures']['divergences'])
        },
        'changelog_accuracy': {
            'operations_detected': results['experiment_5_changelog_accuracy']['operations_detected'],
            'changelog_complete': results['experiment_5_changelog_accuracy']['changelog_complete']
        }
    }

    return summary
