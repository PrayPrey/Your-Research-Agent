"""
Persistence Analyzer for H-M3: Relative advantage tracking across compute budgets.
Tests whether methods show persistent advantages on different metrics.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any
import os

from config import H3Config


class PersistenceAnalyzer:
    """Analyzes persistence of method advantages across compute budgets."""

    def __init__(self, cfg: H3Config):
        self.cfg = cfg

    def compute_relative_advantages(
        self,
        jaccard_by_budget: Dict[int, Dict[str, Any]],
        methods: List[str],
    ) -> Dict[int, Dict[str, str]]:
        """
        Determine which method has lowest mean Jaccard (most disagreement) per budget.

        Note: For H-M3, we track which method pairs show lowest agreement,
        demonstrating persistent paradigm differences.

        Args:
            jaccard_by_budget: {budget: {'matrix': ndarray, 'min': float, 'mean': float}}
            methods: List of method names

        Returns:
            {budget: {'lowest_avg_jaccard_method': method_name, 'lowest_avg_value': float}}
        """
        advantages = {}
        for budget, data in jaccard_by_budget.items():
            matrix = data['matrix']
            n_methods = len(methods)

            # Compute average Jaccard for each method (off-diagonal)
            avg_jaccard = []
            for i in range(n_methods):
                off_diag = [matrix[i, j] for j in range(n_methods) if i != j]
                avg_jaccard.append(np.mean(off_diag))

            # Method with lowest average Jaccard (most disagreement with others)
            min_idx = np.argmin(avg_jaccard)
            advantages[budget] = {
                'lowest_avg_jaccard_method': methods[min_idx],
                'lowest_avg_value': avg_jaccard[min_idx],
            }

        return advantages

    def check_persistence(
        self,
        advantages: Dict[int, Dict[str, str]],
    ) -> Dict[str, Dict[str, bool]]:
        """
        Check which methods show persistent relative advantages.

        A method is persistent if it has the lowest average Jaccard
        (most disagreement) in >60% of budgets.

        Args:
            advantages: {budget: {'lowest_avg_jaccard_method': method, ...}}

        Returns:
            {'persistent_methods': {method: is_persistent}}
        """
        budgets = list(advantages.keys())
        n_budgets = len(budgets)
        threshold = self.cfg.persistence_threshold

        # Count wins per method
        method_wins = {}
        for budget_data in advantages.values():
            method = budget_data['lowest_avg_jaccard_method']
            method_wins[method] = method_wins.get(method, 0) + 1

        # Check persistence
        persistence = {}
        for method, wins in method_wins.items():
            win_rate = wins / n_budgets
            persistence[method] = win_rate > threshold

        return {'persistent_methods': persistence}

    def compute_paradigm_consistency(
        self,
        jaccard_by_budget: Dict[int, Dict[str, Any]],
        methods: List[str],
    ) -> Dict[str, Any]:
        """
        Analyze whether method disagreements are consistent across budgets.

        Methods with similar design paradigms should have higher Jaccard.
        Different paradigms should have persistent disagreement.

        Paradigm groups (based on design):
        - Random projection: TRAK
        - HVP iteration: IF
        - Gradient similarity: TracIn, FastIF
        """
        paradigms = {
            'TRAK': 'random_projection',
            'TracIn': 'gradient_similarity',
            'IF': 'hvp_iteration',
            'FastIF': 'gradient_similarity',
        }

        # Compute cross-paradigm vs same-paradigm Jaccard
        cross_paradigm_jaccards = []
        same_paradigm_jaccards = []

        for budget, data in jaccard_by_budget.items():
            matrix = data['matrix']
            n_methods = len(methods)

            for i in range(n_methods):
                for j in range(i + 1, n_methods):
                    m1, m2 = methods[i], methods[j]
                    jac = matrix[i, j]

                    if paradigms.get(m1) == paradigms.get(m2):
                        same_paradigm_jaccards.append(jac)
                    else:
                        cross_paradigm_jaccards.append(jac)

        return {
            'cross_paradigm_mean': np.mean(cross_paradigm_jaccards) if cross_paradigm_jaccards else None,
            'same_paradigm_mean': np.mean(same_paradigm_jaccards) if same_paradigm_jaccards else None,
            'paradigm_gap': (
                np.mean(same_paradigm_jaccards) - np.mean(cross_paradigm_jaccards)
                if same_paradigm_jaccards and cross_paradigm_jaccards else None
            ),
        }

    def save_results(
        self,
        advantages: Dict[int, Dict[str, str]],
        persistence: Dict[str, Dict[str, bool]],
        paradigm_analysis: Dict[str, Any],
        jaccard_by_budget: Dict[int, Dict[str, Any]],
        methods: List[str],
    ) -> str:
        """Save all persistence analysis results to CSV."""
        # Build advantage rows
        rows = []
        for budget, data in sorted(advantages.items()):
            rows.append({
                'budget': budget,
                'lowest_avg_jaccard_method': data['lowest_avg_jaccard_method'],
                'lowest_avg_value': data['lowest_avg_value'],
                'min_jaccard': jaccard_by_budget[budget]['min'],
                'mean_jaccard': jaccard_by_budget[budget]['mean'],
            })

        df = pd.DataFrame(rows)
        output_path = os.path.join(self.cfg.results_dir, 'metric_advantages.csv')
        df.to_csv(output_path, index=False)

        # Save summary
        summary_path = os.path.join(self.cfg.results_dir, 'persistence_summary.txt')
        with open(summary_path, 'w') as f:
            f.write("=== H-M3 Persistence Analysis ===\n\n")
            f.write("Persistent Methods (>60% budget dominance):\n")
            for method, is_persistent in persistence['persistent_methods'].items():
                f.write(f"  {method}: {'Yes' if is_persistent else 'No'}\n")

            f.write(f"\nParadigm Analysis:\n")
            f.write(f"  Cross-paradigm mean Jaccard: {paradigm_analysis['cross_paradigm_mean']:.4f}\n")
            f.write(f"  Same-paradigm mean Jaccard: {paradigm_analysis['same_paradigm_mean']:.4f}\n")
            f.write(f"  Paradigm gap: {paradigm_analysis['paradigm_gap']:.4f}\n")

        return output_path
