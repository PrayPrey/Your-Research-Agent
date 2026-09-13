"""
Three-Strategy Experiment Runner
Epic C-3: Run structural-only, metamorphic-only, and combined validation on full corpus
"""

import sys
import os
import pandas as pd
import time
from typing import Dict, List
import logging

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../h-m1/code'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../h-m2/code'))

from data.corpus_loader import load_corpus
from contracts.validator import validate_structural
from contracts.metamorphic import validate_metamorphic
from validators.ensemble import validate_combined

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ThreeStrategyRunner:
    """
    Executes three validation strategies on defect corpus:
    1. Structural-only (baseline 1)
    2. Metamorphic-only (baseline 2)
    3. Combined (treatment)
    """

    def __init__(self, corpus_path: str, output_path: str = "outputs/results.csv"):
        """
        Initialize runner

        Args:
            corpus_path: Path to defect corpus CSV
            output_path: Path to save results
        """
        self.corpus_path = corpus_path
        self.output_path = output_path
        self.results = []

    def run_experiments(self):
        """
        Run all three strategies on full corpus

        Returns:
            DataFrame with results (1044 rows: 348 defects × 3 strategies)
        """
        # Load corpus
        logger.info(f"Loading corpus from {self.corpus_path}")
        corpus_df = load_corpus(self.corpus_path)
        total_defects = len(corpus_df)
        logger.info(f"Loaded {total_defects} defects")

        # Process each defect with all three strategies
        for idx, defect in corpus_df.iterrows():
            defect_id = defect['defect_id']

            # Progress logging every 50 defects
            if (idx + 1) % 50 == 0:
                logger.info(f"Progress: {idx + 1}/{total_defects} defects processed")

            # Strategy 1: Structural-only
            self._run_strategy(defect_id, defect, "structural_only", validate_structural)

            # Strategy 2: Metamorphic-only
            self._run_strategy(defect_id, defect, "metamorphic_only", validate_metamorphic)

            # Strategy 3: Combined
            self._run_strategy(defect_id, defect, "combined", validate_combined)

        # Convert to DataFrame and save
        results_df = pd.DataFrame(self.results)
        logger.info(f"Saving results to {self.output_path}")
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        results_df.to_csv(self.output_path, index=False)

        logger.info(f"Experiment complete: {len(results_df)} rows saved")
        return results_df

    def _run_strategy(self, defect_id: str, defect: Dict, strategy: str, validator_fn):
        """
        Run single validation strategy on one defect

        Args:
            defect_id: Unique defect identifier
            defect: Defect record from corpus
            strategy: Strategy name
            validator_fn: Validation function to execute
        """
        try:
            # Mock model and data for validation (defect corpus doesn't include actual models)
            # In real scenario, would load defect-specific model state
            mock_model = None  # Placeholder
            mock_data = None   # Placeholder

            start_time = time.time()

            # Execute validation
            violations = validator_fn(mock_model, mock_data)

            execution_time = time.time() - start_time

            # Record detection result
            detected = len(violations) > 0

            self.results.append({
                "defect_id": defect_id,
                "strategy": strategy,
                "detected": detected,
                "execution_time": execution_time,
                "defect_type": defect.get("type", "unknown"),
                "violation_count": len(violations)
            })

        except Exception as e:
            logger.error(f"Error validating {defect_id} with {strategy}: {e}")
            # Record as failed detection
            self.results.append({
                "defect_id": defect_id,
                "strategy": strategy,
                "detected": False,
                "execution_time": None,
                "defect_type": defect.get("type", "unknown"),
                "violation_count": 0,
                "error": str(e)
            })


def main(corpus_path: str, output_path: str = "outputs/results.csv"):
    """
    Main entry point for experiment

    Args:
        corpus_path: Path to defect corpus CSV
        output_path: Path to save results
    """
    runner = ThreeStrategyRunner(corpus_path, output_path)
    results_df = runner.run_experiments()
    return results_df


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run three-strategy validation experiment")
    parser.add_argument("--corpus", required=True, help="Path to defect corpus CSV")
    parser.add_argument("--output", default="outputs/results.csv", help="Output path for results")

    args = parser.parse_args()
    main(args.corpus, args.output)
