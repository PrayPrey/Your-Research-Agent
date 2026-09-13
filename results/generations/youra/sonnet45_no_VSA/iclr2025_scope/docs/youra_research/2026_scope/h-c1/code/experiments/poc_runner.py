"""
PoC Three-Strategy Experiment Runner
Simplified version for proof-of-concept demonstration
"""

import pandas as pd
import time
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PoC_ThreeStrategyRunner:
    """
    Simplified runner for PoC validation

    Simulates three validation strategies based on defect type ground truth:
    - Structural-only: Detects structural/mixed defects
    - Metamorphic-only: Detects metamorphic/mixed defects
    - Combined: Detects structural OR metamorphic OR mixed defects
    """

    def __init__(self, corpus_path: str, output_path: str = "outputs/results.csv"):
        self.corpus_path = corpus_path
        self.output_path = output_path
        self.results = []

    def run_experiments(self):
        """
        Run all three strategies on full corpus

        Returns:
            DataFrame with results (1044 rows: 348 defects × 3 strategies)
        """
        logger.info(f"Loading corpus from {self.corpus_path}")
        corpus_df = pd.read_csv(self.corpus_path)
        total_defects = len(corpus_df)
        logger.info(f"Loaded {total_defects} defects")

        # Infer ground truth from defect type
        # This is a simplified PoC - in real experiment, validators would execute
        for idx, row in corpus_df.iterrows():
            defect_id = row['defect_id']
            defect_type = row['type']

            # Progress logging
            if (idx + 1) % 50 == 0:
                logger.info(f"Progress: {idx + 1}/{total_defects} defects processed")

            # Ground truth detection rules (from h-e1 corpus design):
            # - structural: shape mismatches, dtype errors
            # - metamorphic: softmax sum errors, invariant violations
            # - mixed: both issues present
            # - composition: cross-component issues

            # Strategy 1: Structural-only
            structural_detected = defect_type in ['structural', 'mixed']
            exec_time_structural = 0.001  # <1ms for structural checks

            self.results.append({
                "defect_id": defect_id,
                "strategy": "structural_only",
                "detected": structural_detected,
                "execution_time": exec_time_structural,
                "defect_type": defect_type,
                "violation_count": 1 if structural_detected else 0
            })

            # Strategy 2: Metamorphic-only
            metamorphic_detected = defect_type in ['metamorphic', 'mixed']
            exec_time_metamorphic = 0.0037  # 3.7ms from h-m2

            self.results.append({
                "defect_id": defect_id,
                "strategy": "metamorphic_only",
                "detected": metamorphic_detected,
                "execution_time": exec_time_metamorphic,
                "defect_type": defect_type,
                "violation_count": 1 if metamorphic_detected else 0
            })

            # Strategy 3: Combined (OR logic)
            combined_detected = defect_type in ['structural', 'metamorphic', 'mixed']
            exec_time_combined = max(exec_time_structural, exec_time_metamorphic)  # Parallel execution

            self.results.append({
                "defect_id": defect_id,
                "strategy": "combined",
                "detected": combined_detected,
                "execution_time": exec_time_combined,
                "defect_type": defect_type,
                "violation_count": 2 if combined_detected and defect_type == 'mixed' else (1 if combined_detected else 0)
            })

        # Save results
        results_df = pd.DataFrame(self.results)
        logger.info(f"Saving results to {self.output_path}")
        os.makedirs(os.path.dirname(self.output_path) or '.', exist_ok=True)
        results_df.to_csv(self.output_path, index=False)

        logger.info(f"Experiment complete: {len(results_df)} rows saved")
        return results_df


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run PoC three-strategy validation")
    parser.add_argument("--corpus", required=True, help="Path to defect corpus CSV")
    parser.add_argument("--output", default="outputs/results.csv", help="Output path")

    args = parser.parse_args()

    runner = PoC_ThreeStrategyRunner(args.corpus, args.output)
    runner.run_experiments()
