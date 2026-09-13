"""
Generalization Analyzer for h-m-integrated
Repository stratification and scaffolding effect analysis
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.metrics import normalized_mutual_info_score
from typing import Dict, List


class GeneralizationAnalyzer:
    """Repository stratification and scaffolding effect analysis."""

    def __init__(self, config):
        """
        Initialize generalization analyzer.

        Args:
            config: ExperimentConfig instance
        """
        self.config = config
        self.gen_config = config.generalization

    def train_repository_probes(
        self,
        embeddings: np.ndarray,
        labels: np.ndarray,
        repositories: np.ndarray
    ) -> Dict[str, float]:
        """
        Train repository-specific linear probes.

        Args:
            embeddings: [N, 384] embeddings
            labels: [N] true labels
            repositories: [N] repository names

        Returns:
            Dict[str, float]: Probe accuracies per repository
        """
        print("\nTraining repository-specific probes...")

        probe_accuracies = {}
        for repo in self.gen_config.repositories:
            # Get samples for this repository
            repo_mask = repositories == repo
            if not repo_mask.any():
                print(f"  Warning: No samples found for repository '{repo}'")
                continue

            repo_embeddings = embeddings[repo_mask]
            repo_labels = labels[repo_mask]

            if len(np.unique(repo_labels)) < 2:
                print(f"  {repo}: Skipped (only one class present)")
                continue

            # Train probe with cross-validation
            probe = LogisticRegression(
                max_iter=self.gen_config.probe_max_iter,
                random_state=self.gen_config.probe_random_state
            )

            try:
                cv_scores = cross_val_score(
                    probe,
                    repo_embeddings,
                    repo_labels,
                    cv=min(self.gen_config.probe_cv_folds, len(repo_labels)),
                    n_jobs=-1
                )
                probe_accuracy = cv_scores.mean()
                probe_accuracies[repo] = float(probe_accuracy)
                print(f"  {repo}: {probe_accuracy:.4f} (±{cv_scores.std():.4f})")

            except Exception as e:
                print(f"  {repo}: Failed - {str(e)}")

        return probe_accuracies

    def compute_probe_variance(self, probe_results: Dict[str, float]) -> float:
        """
        Compute variance of probe accuracies.

        Args:
            probe_results: Dict of repository -> accuracy

        Returns:
            float: Variance of probe accuracies
        """
        if not probe_results:
            return 0.0

        accuracies = list(probe_results.values())
        variance = float(np.var(accuracies))

        print(f"\nProbe accuracy variance: {variance:.4f}")
        return variance

    def compute_repository_nmi(
        self,
        labels_true: np.ndarray,
        labels_pred: np.ndarray,
        repositories: np.ndarray
    ) -> Dict[str, float]:
        """
        Compute NMI per repository.

        Args:
            labels_true: True labels
            labels_pred: Predicted labels
            repositories: Repository names

        Returns:
            Dict[str, float]: NMI per repository
        """
        print("\nComputing repository-specific NMI...")

        repository_nmis = {}
        for repo in self.gen_config.repositories:
            repo_mask = repositories == repo
            if not repo_mask.any():
                continue

            repo_true = labels_true[repo_mask]
            repo_pred = labels_pred[repo_mask]

            if len(np.unique(repo_true)) < 2 or len(np.unique(repo_pred)) < 2:
                print(f"  {repo}: Skipped (insufficient diversity)")
                continue

            nmi = normalized_mutual_info_score(repo_true, repo_pred, average_method='arithmetic')
            repository_nmis[repo] = float(nmi)
            print(f"  {repo}: {nmi:.4f}")

        return repository_nmis

    def analyze_scaffolding_effect(
        self,
        labels_true: np.ndarray,
        labels_pred: np.ndarray,
        scaffolding: np.ndarray
    ) -> Dict[str, float]:
        """
        Compare NMI for scaffolded vs unscaffolded samples.

        Args:
            labels_true: True labels
            labels_pred: Predicted labels
            scaffolding: Binary array (0=unscaffolded, 1=scaffolded)

        Returns:
            Dict[str, float]: NMI for scaffolded, unscaffolded, and gap
        """
        print("\nAnalyzing scaffolding effect...")

        # Scaffolded samples
        scaffolded_mask = scaffolding == 1
        if scaffolded_mask.any():
            scaffolded_true = labels_true[scaffolded_mask]
            scaffolded_pred = labels_pred[scaffolded_mask]

            if len(np.unique(scaffolded_true)) >= 2 and len(np.unique(scaffolded_pred)) >= 2:
                nmi_scaffolded = normalized_mutual_info_score(
                    scaffolded_true, scaffolded_pred, average_method='arithmetic'
                )
            else:
                nmi_scaffolded = 0.0
                print("  Warning: Scaffolded samples have insufficient diversity")
        else:
            nmi_scaffolded = 0.0
            print("  Warning: No scaffolded samples found")

        # Unscaffolded samples
        unscaffolded_mask = scaffolding == 0
        if unscaffolded_mask.any():
            unscaffolded_true = labels_true[unscaffolded_mask]
            unscaffolded_pred = labels_pred[unscaffolded_mask]

            if len(np.unique(unscaffolded_true)) >= 2 and len(np.unique(unscaffolded_pred)) >= 2:
                nmi_unscaffolded = normalized_mutual_info_score(
                    unscaffolded_true, unscaffolded_pred, average_method='arithmetic'
                )
            else:
                nmi_unscaffolded = 0.0
                print("  Warning: Unscaffolded samples have insufficient diversity")
        else:
            nmi_unscaffolded = 0.0
            print("  Warning: No unscaffolded samples found")

        # Compute gap
        scaffolding_gap = nmi_scaffolded - nmi_unscaffolded

        results = {
            'scaffolded': float(nmi_scaffolded),
            'unscaffolded': float(nmi_unscaffolded),
            'gap': float(scaffolding_gap)
        }

        print(f"  Scaffolded NMI: {nmi_scaffolded:.4f}")
        print(f"  Unscaffolded NMI: {nmi_unscaffolded:.4f}")
        print(f"  Scaffolding gap: {scaffolding_gap:.4f}")

        return results
