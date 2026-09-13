"""
Statistical validator for h-m2 temporal lead time validation.
McNemar test and permutation baseline for significance testing.
"""
import numpy as np
import json
from typing import Dict, List
from scipy.stats import binomtest
from config import SIGNIFICANCE_LEVEL, PERMUTATION_ITERATIONS, RANDOM_SEED


class StatisticalValidator:
    """Statistical validation for temporal lead times."""

    def __init__(self, alpha: float = SIGNIFICANCE_LEVEL, seed: int = RANDOM_SEED):
        """
        Initialize statistical validator.

        Args:
            alpha: Significance level
            seed: Random seed for permutation tests
        """
        self.alpha = alpha
        np.random.seed(seed)

    def mcnemar_test(self, lead_times: List[dict]) -> Dict[str, float]:
        """
        Test whether temporal precedence significantly exceeds chance.

        Uses binomial test (appropriate for small samples):
        H0: p(precede) = 0.5 (random timing)
        H1: p(precede) > 0.5 (temporal precedence)

        Args:
            lead_times: List of lead time results with 'precedes' field

        Returns:
            Dict with test statistics and p-value
        """
        n_total = len(lead_times)
        n_precede = sum(lt['precedes'] for lt in lead_times)
        n_lag = n_total - n_precede

        # Binomial test (one-sided, greater)
        # ponytail: Use binomtest instead of McNemar for small samples
        p_value = binomtest(n_precede, n_total, 0.5, alternative='greater').pvalue

        result = {
            'test': 'binomial_test',
            'n_total': int(n_total),
            'n_precede': int(n_precede),
            'n_lag': int(n_lag),
            'p_value': float(p_value),
            'significant': bool(p_value < self.alpha)
        }

        print(f"Binomial test: {n_precede}/{n_total} precede, p={p_value:.4f}")
        return result

    def permutation_baseline(
        self,
        saturation_dates: Dict[str, str],
        adoption_dates: Dict[str, str],
        pairs: List[tuple],
        n_iter: int = PERMUTATION_ITERATIONS
    ) -> Dict[str, float]:
        """
        Permutation test: shuffle saturation dates to assess chance baseline.

        Args:
            saturation_dates: Dict of {benchmark: date}
            adoption_dates: Dict of {shift: date}
            pairs: List of (benchmark, shift) tuples
            n_iter: Number of permutations

        Returns:
            Dict with permutation test results
        """
        import pandas as pd
        from config import LEAD_TIME_THRESHOLD

        # Observed precede fraction
        observed_precede = self._compute_precede_fraction(
            saturation_dates, adoption_dates, pairs
        )

        # Permutation test
        random_precede_fractions = []
        benchmarks = list(saturation_dates.keys())
        dates = list(saturation_dates.values())

        for _ in range(n_iter):
            # Shuffle saturation dates
            shuffled_dates = np.random.permutation(dates)
            shuffled_saturation = dict(zip(benchmarks, shuffled_dates))

            # Compute precede fraction
            precede_frac = self._compute_precede_fraction(
                shuffled_saturation, adoption_dates, pairs
            )
            random_precede_fractions.append(precede_frac)

        # p-value: fraction of permutations >= observed
        p_value = sum(r >= observed_precede for r in random_precede_fractions) / n_iter

        result = {
            'test': 'permutation',
            'n_iterations': int(n_iter),
            'observed_precede_fraction': float(observed_precede),
            'random_mean': float(np.mean(random_precede_fractions)),
            'random_std': float(np.std(random_precede_fractions)),
            'p_value': float(p_value),
            'significant': bool(p_value < self.alpha)
        }

        print(f"Permutation test: observed={observed_precede:.2%}, random_mean={result['random_mean']:.2%}, p={p_value:.4f}")
        return result

    def _compute_precede_fraction(
        self,
        saturation_dates: Dict[str, str],
        adoption_dates: Dict[str, str],
        pairs: List[tuple]
    ) -> float:
        """Helper to compute precede fraction for given date mappings."""
        import pandas as pd
        from config import LEAD_TIME_THRESHOLD

        precede_count = 0
        total = 0

        for benchmark, shift in pairs:
            if benchmark not in saturation_dates or shift not in adoption_dates:
                continue

            sat_date = pd.to_datetime(saturation_dates[benchmark])
            adopt_date = pd.to_datetime(adoption_dates[shift])
            lead_months = (adopt_date - sat_date) / pd.Timedelta(days=30.44)

            if lead_months > LEAD_TIME_THRESHOLD:
                precede_count += 1
            total += 1

        return precede_count / total if total > 0 else 0.0

    def compute_effect_size(self, lead_times: List[dict]) -> float:
        """
        Compute effect size (Cohen's h) for temporal precedence.

        Args:
            lead_times: List of lead time results

        Returns:
            Cohen's h effect size
        """
        n_precede = sum(lt['precedes'] for lt in lead_times)
        n_total = len(lead_times)

        p_observed = n_precede / n_total
        p_null = 0.5  # Chance baseline

        # Cohen's h = 2 * (arcsin(sqrt(p1)) - arcsin(sqrt(p2)))
        h = 2 * (np.arcsin(np.sqrt(p_observed)) - np.arcsin(np.sqrt(p_null)))
        return float(h)


if __name__ == "__main__":
    from pathlib import Path
    from lead_time_analyzer import LeadTimeAnalyzer
    from config import BENCHMARK_SHIFT_PAIRS

    # Load lead times
    results_dir = Path(__file__).parent.parent / "results"
    with open(results_dir / "lead_times.json") as f:
        lead_time_results = json.load(f)

    lead_times = lead_time_results['pairs']

    # Load dates for permutation test
    analyzer = LeadTimeAnalyzer()
    saturation_dates = analyzer.load_saturation_dates()

    data_dir = Path(__file__).parent.parent / "data"
    with open(data_dir / "shift_adoption_dates.json") as f:
        adoption_dates = json.load(f)

    # Run statistical tests
    validator = StatisticalValidator()

    # Binomial test
    binomial_result = validator.mcnemar_test(lead_times)

    # Permutation test
    permutation_result = validator.permutation_baseline(
        saturation_dates, adoption_dates, BENCHMARK_SHIFT_PAIRS
    )

    # Effect size
    effect_size = validator.compute_effect_size(lead_times)
    print(f"Effect size (Cohen's h): {effect_size:.3f}")

    # Save validation results
    validation_results = {
        'binomial_test': binomial_result,
        'permutation_test': permutation_result,
        'effect_size': effect_size
    }

    output_file = results_dir / "statistical_validation.json"
    with open(output_file, 'w') as f:
        json.dump(validation_results, f, indent=2)

    print(f"\nSaved validation results to {output_file}")
