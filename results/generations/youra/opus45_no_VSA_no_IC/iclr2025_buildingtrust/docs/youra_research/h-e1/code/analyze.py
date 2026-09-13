"""Correlation analysis for H-E1: BenchmarkCorrelationAnalyzer."""

import pandas as pd
import numpy as np
from scipy import stats
from itertools import combinations
from config import BENCHMARKS, BASELINE_PAIR, CORR_UPPER_BOUND, ALPHA, CI_LEVEL


class BenchmarkCorrelationAnalyzer:
    """Analyze correlations between truthfulness benchmarks."""

    def __init__(self, benchmark_scores: pd.DataFrame):
        """benchmark_scores: output of load_benchmark_scores()."""
        self.scores = benchmark_scores
        self.benchmarks = BENCHMARKS  # ["truthfulqa", "halueval", "factscore"]
        self._validate_columns()

    def _validate_columns(self):
        """Ensure required columns exist."""
        required = self.benchmarks + list(BASELINE_PAIR)
        missing = [c for c in required if c not in self.scores.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

    def _pair_key(self, a: str, b: str) -> str:
        """Format pair key consistently (alphabetical order)."""
        return f"{min(a,b)}-{max(a,b)}"

    def compute_correlation_matrix(self) -> pd.DataFrame:
        """Spearman r for all pairs in self.benchmarks. Returns 3x3 symmetric DataFrame."""
        subset = self.scores[self.benchmarks]
        corr_matrix = subset.corr(method="spearman")
        return corr_matrix

    def compute_baseline_correlation(self) -> float:
        """r(mmlu_physics, halueval) via config.BASELINE_PAIR."""
        x = self.scores[BASELINE_PAIR[0]]
        y = self.scores[BASELINE_PAIR[1]]
        r, _ = stats.spearmanr(x, y)
        return r

    def compute_pvalues(self) -> dict:
        """p-value per pair from spearmanr."""
        pvalues = {}
        for a, b in combinations(self.benchmarks, 2):
            _, p = stats.spearmanr(self.scores[a], self.scores[b])
            pvalues[self._pair_key(a, b)] = p
        return pvalues

    def apply_bonferroni(self, pvalues: dict) -> dict:
        """adjusted_p = min(p * len(pvalues), 1.0) per pair."""
        n = len(pvalues)
        return {k: min(p * n, 1.0) for k, p in pvalues.items()}

    def compute_confidence_intervals(self) -> dict:
        """95% CI via Fisher z-transform."""
        n = len(self.scores)
        ci = {}

        for a, b in combinations(self.benchmarks, 2):
            r, _ = stats.spearmanr(self.scores[a], self.scores[b])

            # Fisher z-transform
            z = np.arctanh(r)
            se = 1.0 / np.sqrt(n - 3)

            # CI in z-space
            z_crit = stats.norm.ppf((1 + CI_LEVEL) / 2)
            z_lower = z - z_crit * se
            z_upper = z + z_crit * se

            # Transform back to r-space
            r_lower = np.tanh(z_lower)
            r_upper = np.tanh(z_upper)

            ci[self._pair_key(a, b)] = (round(r_lower, 4), round(r_upper, 4))

        return ci

    def evaluate_hypothesis(self) -> dict:
        """
        Evaluate gate condition: baseline_r < r < 0.7 for all cross-benchmark pairs.

        Returns {
          "passed": bool,
          "correlations": dict[str, float],
          "baseline_r": float,
          "threshold_upper": float,
          "pvalues": dict[str, float],
          "adjusted_pvalues": dict[str, float],
          "ci": dict[str, tuple[float, float]],
          "n_models": int,
        }
        """
        corr_matrix = self.compute_correlation_matrix()
        baseline_r = self.compute_baseline_correlation()
        pvalues = self.compute_pvalues()
        adj_pvalues = self.apply_bonferroni(pvalues)
        ci = self.compute_confidence_intervals()

        # Extract pairwise correlations
        correlations = {}
        for a, b in combinations(self.benchmarks, 2):
            key = self._pair_key(a, b)
            correlations[key] = round(corr_matrix.loc[a, b], 4)

        # Gate check: all cross-benchmark r must satisfy baseline_r < r < CORR_UPPER_BOUND
        passed = all(
            baseline_r < r < CORR_UPPER_BOUND
            for r in correlations.values()
        )

        return {
            "passed": passed,
            "correlations": correlations,
            "baseline_r": round(baseline_r, 4),
            "threshold_upper": CORR_UPPER_BOUND,
            "pvalues": {k: round(v, 6) for k, v in pvalues.items()},
            "adjusted_pvalues": {k: round(v, 6) for k, v in adj_pvalues.items()},
            "ci": ci,
            "n_models": len(self.scores),
        }


if __name__ == "__main__":
    from data import load_benchmark_scores

    scores = load_benchmark_scores()
    analyzer = BenchmarkCorrelationAnalyzer(scores)
    result = analyzer.evaluate_hypothesis()

    print("\n=== Hypothesis Evaluation ===")
    print(f"N models: {result['n_models']}")
    print(f"Baseline r (mmlu_physics-halueval): {result['baseline_r']}")
    print(f"Upper threshold: {result['threshold_upper']}")
    print("\nCross-benchmark correlations:")
    for pair, r in result["correlations"].items():
        ci = result["ci"][pair]
        p = result["adjusted_pvalues"][pair]
        print(f"  {pair}: r={r:.4f} (95% CI: [{ci[0]:.4f}, {ci[1]:.4f}], p_adj={p:.6f})")
    print(f"\nGate: {'PASS' if result['passed'] else 'FAIL'}")
