"""
FNR Metrics Calculator - Epic C-4
Calculate FNR, bootstrap 95% CI, and McNemar test for three-strategy comparison
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, Tuple, List
from dataclasses import dataclass


@dataclass
class FNRMetrics:
    """False-Negative Rate metrics with statistical tests"""
    strategy: str
    fnr: float
    fnr_ci_lower: float
    fnr_ci_upper: float
    detection_rate: float
    total_defects: int
    detected_defects: int
    missed_defects: int


class FNRAnalyzer:
    """
    Statistical analyzer for three-strategy experiment
    Calculates FNR, bootstrap CI, and McNemar test
    """

    def __init__(self, results_df: pd.DataFrame):
        """
        Initialize analyzer

        Args:
            results_df: Results from ThreeStrategyRunner (348 defects × 3 strategies)
        """
        self.results_df = results_df

    def calculate_fnr_all_strategies(self) -> Dict[str, FNRMetrics]:
        """
        Calculate FNR for all three strategies

        Returns:
            Dict mapping strategy name to FNRMetrics
        """
        metrics = {}

        for strategy in ["structural_only", "metamorphic_only", "combined"]:
            strategy_df = self.results_df[self.results_df["strategy"] == strategy]

            total = len(strategy_df)
            detected = strategy_df["detected"].sum()
            missed = total - detected

            fnr = missed / total if total > 0 else 0.0

            # Bootstrap 95% CI
            ci_lower, ci_upper = self.bootstrap_confidence_interval(
                strategy_df["detected"].values, n_iterations=1000
            )

            metrics[strategy] = FNRMetrics(
                strategy=strategy,
                fnr=fnr,
                fnr_ci_lower=ci_lower,
                fnr_ci_upper=ci_upper,
                detection_rate=detected / total if total > 0 else 0.0,
                total_defects=total,
                detected_defects=detected,
                missed_defects=missed
            )

        return metrics

    def bootstrap_confidence_interval(
        self,
        detected_array: np.ndarray,
        n_iterations: int = 1000,
        confidence: float = 0.95
    ) -> Tuple[float, float]:
        """
        Calculate bootstrap 95% CI for FNR

        Args:
            detected_array: Boolean array of detection results
            n_iterations: Number of bootstrap iterations
            confidence: Confidence level (default 0.95)

        Returns:
            Tuple of (lower_bound, upper_bound) for FNR
        """
        n_samples = len(detected_array)
        fnr_samples = []

        for _ in range(n_iterations):
            # Resample with replacement
            resampled = np.random.choice(detected_array, size=n_samples, replace=True)
            detected = resampled.sum()
            missed = n_samples - detected
            fnr = missed / n_samples
            fnr_samples.append(fnr)

        # Calculate percentile-based CI
        alpha = (1 - confidence) / 2
        ci_lower = np.percentile(fnr_samples, alpha * 100)
        ci_upper = np.percentile(fnr_samples, (1 - alpha) * 100)

        return ci_lower, ci_upper

    def mcnemar_test(self, baseline_strategy: str, treatment_strategy: str = "combined") -> Dict:
        """
        McNemar's test for paired proportions

        Args:
            baseline_strategy: Baseline strategy name
            treatment_strategy: Treatment strategy name (default: combined)

        Returns:
            Dict with test statistic and p-value
        """
        # Get detection results for both strategies
        baseline_df = self.results_df[self.results_df["strategy"] == baseline_strategy]
        treatment_df = self.results_df[self.results_df["strategy"] == treatment_strategy]

        # Ensure same defect ordering
        baseline_df = baseline_df.sort_values("defect_id")
        treatment_df = treatment_df.sort_values("defect_id")

        baseline_detected = baseline_df["detected"].values
        treatment_detected = treatment_df["detected"].values

        # Build contingency table
        # Rows: baseline, Columns: treatment
        # Cell [0,0]: both miss, [0,1]: baseline miss/treatment detect
        # Cell [1,0]: baseline detect/treatment miss, [1,1]: both detect
        both_detected = ((baseline_detected == 1) & (treatment_detected == 1)).sum()
        baseline_only = ((baseline_detected == 1) & (treatment_detected == 0)).sum()
        treatment_only = ((baseline_detected == 0) & (treatment_detected == 1)).sum()
        both_missed = ((baseline_detected == 0) & (treatment_detected == 0)).sum()

        # McNemar's test focuses on discordant pairs (baseline_only, treatment_only)
        # Test statistic: (|b - c| - 1)^2 / (b + c), where b=baseline_only, c=treatment_only
        b = baseline_only
        c = treatment_only

        if (b + c) == 0:
            # No discordant pairs - perfect agreement
            statistic = 0.0
            p_value = 1.0
        else:
            statistic = ((abs(b - c) - 1) ** 2) / (b + c)
            # Chi-square distribution with 1 df
            p_value = 1 - stats.chi2.cdf(statistic, df=1)

        return {
            "baseline": baseline_strategy,
            "treatment": treatment_strategy,
            "statistic": statistic,
            "p_value": p_value,
            "significant": p_value < 0.05,
            "both_detected": both_detected,
            "baseline_only": baseline_only,
            "treatment_only": treatment_only,
            "both_missed": both_missed
        }

    def fnr_reduction_percentage(
        self,
        baseline_strategy: str,
        treatment_strategy: str = "combined"
    ) -> float:
        """
        Calculate FNR reduction percentage

        Formula: (FNR_baseline - FNR_treatment) / FNR_baseline × 100%

        Args:
            baseline_strategy: Baseline strategy name
            treatment_strategy: Treatment strategy name

        Returns:
            FNR reduction percentage
        """
        metrics = self.calculate_fnr_all_strategies()

        baseline_fnr = metrics[baseline_strategy].fnr
        treatment_fnr = metrics[treatment_strategy].fnr

        if baseline_fnr == 0:
            return 0.0

        reduction = ((baseline_fnr - treatment_fnr) / baseline_fnr) * 100
        return reduction

    def stratified_detection_rates(self) -> pd.DataFrame:
        """
        Calculate detection rates stratified by defect type

        Returns:
            DataFrame with detection rates per defect type per strategy
        """
        grouped = self.results_df.groupby(["strategy", "defect_type"])["detected"].agg(["sum", "count"])
        grouped["detection_rate"] = grouped["sum"] / grouped["count"]
        return grouped.reset_index()


def main(results_path: str):
    """
    Main analysis pipeline

    Args:
        results_path: Path to results CSV from ThreeStrategyRunner
    """
    df = pd.read_csv(results_path)
    analyzer = FNRAnalyzer(df)

    # Calculate FNR for all strategies
    fnr_metrics = analyzer.calculate_fnr_all_strategies()

    print("=" * 60)
    print("FNR Analysis Results")
    print("=" * 60)

    for strategy, metrics in fnr_metrics.items():
        print(f"\nStrategy: {strategy}")
        print(f"  FNR: {metrics.fnr:.2%} (95% CI: [{metrics.fnr_ci_lower:.2%}, {metrics.fnr_ci_upper:.2%}])")
        print(f"  Detection Rate: {metrics.detection_rate:.2%}")
        print(f"  Detected: {metrics.detected_defects}/{metrics.total_defects}")

    # McNemar tests
    print("\n" + "=" * 60)
    print("McNemar Test Results")
    print("=" * 60)

    for baseline in ["structural_only", "metamorphic_only"]:
        result = analyzer.mcnemar_test(baseline, "combined")
        print(f"\n{baseline} vs combined:")
        print(f"  Statistic: {result['statistic']:.3f}")
        print(f"  P-value: {result['p_value']:.4f}")
        print(f"  Significant: {result['significant']}")

    # FNR reduction
    print("\n" + "=" * 60)
    print("FNR Reduction")
    print("=" * 60)

    for baseline in ["structural_only", "metamorphic_only"]:
        reduction = analyzer.fnr_reduction_percentage(baseline, "combined")
        print(f"{baseline} → combined: {reduction:.1f}%")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Analyze FNR results")
    parser.add_argument("--results", required=True, help="Path to results CSV")

    args = parser.parse_args()
    main(args.results)
