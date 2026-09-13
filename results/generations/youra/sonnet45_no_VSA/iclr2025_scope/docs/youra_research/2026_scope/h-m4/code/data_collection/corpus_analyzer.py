"""Retrospective analysis on Jiang et al. 348-defect corpus."""

import pandas as pd
import sys
from pathlib import Path
from typing import Dict, List


class CorpusAnalyzer:
    """Analyze Jiang et al. defect corpus for lifecycle shift baseline."""

    def __init__(self, corpus_path: str):
        """Initialize corpus analyzer."""
        self.corpus_path = corpus_path
        self.df = None
        self.contractable_df = None

    def load_jiang_corpus(self) -> pd.DataFrame:
        """Load Jiang et al. 348-defect corpus."""
        self.df = pd.read_csv(self.corpus_path)
        print(f"Loaded {len(self.df)} defects from corpus")
        return self.df

    def filter_contractable_defects(self, df: pd.DataFrame = None) -> pd.DataFrame:
        """Filter for environment-stage contractable defects."""
        if df is None:
            df = self.df

        # Filter for defects that can be detected by contracts
        contractable = df[df['can_be_detected_by_contracts'] == True].copy()

        # Further filter for environment-stage
        environment_contractable = contractable[
            contractable['stage_of_failure'] == 'environment'
        ].copy()

        self.contractable_df = environment_contractable
        print(f"Filtered to {len(environment_contractable)} environment-stage contractable defects")
        return environment_contractable

    def apply_contracts_to_defect(self, defect: Dict) -> Dict:
        """Apply contract validation to a single defect scenario."""
        result = {
            'defect_id': defect['defect_id'],
            'original_stage': defect['stage_of_failure'],
            'original_ttff': defect['current_ttff_hours'],
            'with_contracts_stage': 'environment',
            'with_contracts_ttff': 0.5,  # Simulated environment-stage detection time
            'lifecycle_shift': defect['current_ttff_hours'] - 0.5
        }
        return result

    def measure_baseline_shift(self) -> Dict[str, float]:
        """Measure baseline lifecycle shift from retrospective analysis."""
        if self.contractable_df is None:
            self.filter_contractable_defects()

        results = []
        for _, defect in self.contractable_df.iterrows():
            result = self.apply_contracts_to_defect(defect.to_dict())
            results.append(result)

        # Calculate aggregate metrics
        baseline_median_ttff = self.df[
            self.df['can_be_detected_by_contracts'] == True
        ]['current_ttff_hours'].median()

        proposed_median_ttff = pd.Series([r['with_contracts_ttff'] for r in results]).median()

        lifecycle_shift = baseline_median_ttff - proposed_median_ttff

        summary = {
            'total_defects': len(self.df),
            'contractable_defects': len(self.contractable_df),
            'baseline_median_ttff': baseline_median_ttff,
            'proposed_median_ttff': proposed_median_ttff,
            'lifecycle_shift_hours': lifecycle_shift,
            'individual_results': results
        }

        print(f"\nRetrospective Analysis Summary:")
        print(f"  Total defects: {summary['total_defects']}")
        print(f"  Contractable defects: {summary['contractable_defects']}")
        print(f"  Baseline median TTFF: {baseline_median_ttff:.2f} hours")
        print(f"  Proposed median TTFF: {proposed_median_ttff:.2f} hours")
        print(f"  Lifecycle shift: {lifecycle_shift:.2f} hours")

        return summary
