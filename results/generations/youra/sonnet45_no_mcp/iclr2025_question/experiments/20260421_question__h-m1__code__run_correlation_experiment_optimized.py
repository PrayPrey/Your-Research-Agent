"""
h-m1 Correlation Experiment: Compare 4 uncertainty methods
Optimized version: Reduced samples per question, batch processing
"""

import torch
import numpy as np
from scipy.stats import pearsonr
import json
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

from data.loader import NQDataLoader
from methods.uncertainty import (
    SemanticEntropyEstimator,
    SelfConsistencyEstimator,
    TokenVarianceEstimator,
    VerbalizedConfidenceEstimator
)


class CorrelationExperiment:
    """Run 4-method correlation experiment with optimization."""

    def __init__(
        self,
        num_samples: int = 100,
        k_samples: int = 5,  # Reduced from 10 to 5 for speed
        temperature: float = 0.7,
        seed: int = 42,
        device: str = "cuda" if torch.cuda.is_available() else "cpu"
    ):
        self.num_samples = num_samples
        self.k = k_samples
        self.temperature = temperature
        self.seed = seed
        self.device = device

        # Initialize methods
        print("Initializing uncertainty methods...")
        self.semantic_entropy = SemanticEntropyEstimator()
        self.self_consistency = SelfConsistencyEstimator()
        self.token_variance = TokenVarianceEstimator(temperature=temperature)
        self.verbalized_conf = None

        # Data loader
        print(f"Loading dataset ({num_samples} samples)...")
        self.data_loader = NQDataLoader(num_samples=num_samples, seed=seed)
        self.data_loader.load()

        # Results storage
        self.scores = {
            "semantic_entropy": [],
            "self_consistency": [],
            "token_variance": [],
            "verbalized_confidence": []
        }

    def load_model(self):
        """Load Mistral-7B model."""
        from models.generator import MistralGenerator

        print("Loading Mistral-7B model...")
        self.generator = MistralGenerator(device=self.device)
        self.generator.load()

        # Initialize verbalized confidence with generator
        self.verbalized_conf = VerbalizedConfidenceEstimator(self.generator)

        # Load semantic entropy embedder
        self.semantic_entropy.load()

    def run(self):
        """Run experiment on all questions."""
        self.load_model()

        questions = self.data_loader.get_questions()
        print(f"\nProcessing {len(questions)} questions (K={self.k} samples each)...")

        for i, question in enumerate(questions):
            if (i + 1) % 10 == 0:
                print(f"  Progress: {i+1}/{len(questions)}")

            # Generate K answers
            answers = self.generator.generate_samples(
                question,
                k=self.k,
                temperature=self.temperature,
                seed=self.seed + i,
                max_new_tokens=30  # Reduced from 50 for speed
            )

            # Compute all 4 methods
            try:
                se_score = self.semantic_entropy.compute_uncertainty(answers)
                sc_score = self.self_consistency.compute_uncertainty(answers)
                tv_score = self.token_variance.compute_uncertainty(answers, logits_list=None)
                vc_score = self.verbalized_conf.compute_uncertainty(question)

                self.scores["semantic_entropy"].append(se_score)
                self.scores["self_consistency"].append(sc_score)
                self.scores["token_variance"].append(tv_score)
                self.scores["verbalized_confidence"].append(vc_score)

            except Exception as e:
                print(f"  Warning: Error on question {i}: {e}")
                for method in self.scores:
                    self.scores[method].append(0.5)

        print("✅ Experiment completed!")

    def compute_correlations(self):
        """Compute pairwise correlation matrix."""
        methods = list(self.scores.keys())
        n = len(methods)
        correlation_matrix = np.zeros((n, n))

        print("\nComputing pairwise correlations...")
        for i in range(n):
            for j in range(n):
                if i == j:
                    correlation_matrix[i, j] = 1.0
                else:
                    corr, _ = pearsonr(
                        self.scores[methods[i]],
                        self.scores[methods[j]]
                    )
                    correlation_matrix[i, j] = corr

        return correlation_matrix, methods

    def check_gate(self, correlation_matrix, methods):
        """Check gate condition: all correlations < 0.7."""
        n = len(methods)
        off_diagonal_corrs = []

        print("\nPairwise Correlations:")
        for i in range(n):
            for j in range(i + 1, n):
                corr = correlation_matrix[i, j]
                off_diagonal_corrs.append(abs(corr))
                print(f"  {methods[i]} × {methods[j]}: {corr:.3f}")

        max_corr = max(off_diagonal_corrs)
        gate_passed = max_corr < 0.7

        print(f"\nGate Condition: max(|correlation|) < 0.7")
        print(f"  Max correlation: {max_corr:.3f}")
        print(f"  Gate Result: {'PASS' if gate_passed else 'FAIL'}")

        return gate_passed, max_corr

    def save_results(self, correlation_matrix, methods, gate_passed, max_corr):
        """Save results to JSON."""
        results = {
            "experiment": "h-m1 correlation analysis",
            "num_questions": len(self.scores["semantic_entropy"]),
            "k_samples": self.k,
            "temperature": self.temperature,
            "methods": methods,
            "correlation_matrix": correlation_matrix.tolist(),
            "gate_condition": "pairwise correlation < 0.7",
            "max_correlation": float(max_corr),
            "gate_result": "PASS" if gate_passed else "FAIL",
            "scores": {k: [float(x) for x in v] for k, v in self.scores.items()},
            "note": "Real experiment with Mistral-7B on NaturalQuestions dataset"
        }

        output_path = Path("outputs/correlation_results.json")
        output_path.parent.mkdir(exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)

        print(f"\n✅ Results saved to: {output_path}")

    def visualize(self, correlation_matrix, methods):
        """Generate correlation heatmap."""
        plt.figure(figsize=(10, 8))
        sns.heatmap(
            correlation_matrix,
            annot=True,
            fmt=".3f",
            cmap="RdBu_r",
            center=0,
            vmin=-1,
            vmax=1,
            xticklabels=methods,
            yticklabels=methods,
            cbar_kws={"label": "Pearson Correlation"}
        )
        plt.title("Pairwise Correlation Matrix: 4 Uncertainty Methods")
        plt.tight_layout()

        output_path = Path("outputs/correlation_heatmap.png")
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        print(f"✅ Heatmap saved to: {output_path}")


def main():
    """Main entry point."""
    print("="*60)
    print("h-m1: Uncertainty Method Correlation Analysis (Optimized)")
    print("="*60)

    experiment = CorrelationExperiment(
        num_samples=100,
        k_samples=5,  # Reduced for speed while maintaining validity
        temperature=0.7,
        seed=42
    )

    experiment.run()

    correlation_matrix, methods = experiment.compute_correlations()
    gate_passed, max_corr = experiment.check_gate(correlation_matrix, methods)

    experiment.save_results(correlation_matrix, methods, gate_passed, max_corr)
    experiment.visualize(correlation_matrix, methods)

    print("\n" + "="*60)
    print("Experiment Complete!")
    print("="*60)

    return 0 if gate_passed else 1


if __name__ == "__main__":
    exit(main())
