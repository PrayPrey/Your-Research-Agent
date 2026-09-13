"""Error signature analyzer for comparing uncertainty patterns across error types."""

from typing import List, Dict
import numpy as np


class ErrorSignatureAnalyzer:
    """Analyze uncertainty signatures across error types."""

    def __init__(self, semantic_estimator, consistency_estimator, generator):
        """
        Initialize analyzer with uncertainty methods.

        Args:
            semantic_estimator: SemanticEntropyEstimator instance
            consistency_estimator: SelfConsistencyEstimator instance
            generator: MistralGenerator instance
        """
        self.semantic = semantic_estimator
        self.consistency = consistency_estimator
        self.generator = generator

    def analyze_dataset(
        self,
        questions: List[str],
        dataset_name: str,
        k: int = 5,
        temperature: float = 0.7
    ) -> Dict[str, List[float]]:
        """
        Compute diversity and agreement scores for dataset.

        Args:
            questions: List[str] - Question list (100 samples)
            dataset_name: str - Dataset identifier for logging
            k: int - Samples per question (default 5)
            temperature: float - Sampling temperature

        Returns:
            Dict with keys: 'diversity', 'agreement'
            Each value: List[float] with scores for all questions
        """
        print(f"\n{'='*60}")
        print(f"Analyzing {dataset_name} ({len(questions)} questions)")
        print(f"{'='*60}")

        diversity_scores = []
        agreement_scores = []

        for idx, question in enumerate(questions):
            if (idx + 1) % 10 == 0:
                print(f"Processing question {idx + 1}/{len(questions)}...")

            # Generate K samples
            answers = self.generator.generate_samples(
                question,
                k=k,
                temperature=temperature,
                seed=42 + idx  # Vary seed per question
            )

            # Compute diversity (semantic entropy)
            diversity = self.semantic.compute_uncertainty(answers)
            diversity_scores.append(diversity)

            # Compute agreement (1 - disagreement from self-consistency)
            disagreement = self.consistency.compute_uncertainty(answers)
            agreement = 1.0 - disagreement
            agreement_scores.append(agreement)

        print(f"Completed {dataset_name} analysis")
        print(f"  Mean diversity: {np.mean(diversity_scores):.4f}")
        print(f"  Mean agreement: {np.mean(agreement_scores):.4f}")

        return {
            'diversity': diversity_scores,
            'agreement': agreement_scores
        }

    def compare_signatures(
        self,
        nq_scores: Dict[str, List[float]],
        tqa_scores: Dict[str, List[float]]
    ) -> Dict[str, any]:
        """
        Compare signatures between datasets.

        Args:
            nq_scores: NaturalQuestions scores
            tqa_scores: TruthfulQA scores

        Returns:
            Dict with keys: 'nq_diversity_mean', 'tqa_diversity_mean',
                           'nq_agreement_mean', 'tqa_agreement_mean'
        """
        return {
            'nq_diversity_mean': np.mean(nq_scores['diversity']),
            'tqa_diversity_mean': np.mean(tqa_scores['diversity']),
            'nq_agreement_mean': np.mean(nq_scores['agreement']),
            'tqa_agreement_mean': np.mean(tqa_scores['agreement'])
        }
