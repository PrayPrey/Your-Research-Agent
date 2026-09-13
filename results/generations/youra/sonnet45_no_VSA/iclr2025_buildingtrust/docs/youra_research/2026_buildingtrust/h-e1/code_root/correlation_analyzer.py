"""Statistical correlation analysis for H-E1 Cross-Benchmark Analysis."""

import pandas as pd
import numpy as np
from scipy.stats import spearmanr
from typing import Dict, Tuple, Any


class CorrelationAnalyzer:
    """Statistical correlation analyzer for benchmark rankings."""

    def __init__(self, significance_level: float = 0.01):
        self.significance_level = significance_level

    def compute_spearman(self, rank1: pd.Series, rank2: pd.Series) -> Tuple[float, float]:
        """Compute Spearman ρ. rank1, rank2: [N] -> (ρ, p-value)"""
        rho, pvalue = spearmanr(rank1, rank2, nan_policy='omit')
        return rho, pvalue

    def compute_pairwise_correlations(
        self, rankings: Dict[str, pd.Series]
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Compute all pairs. Returns: (corr_matrix, pvalue_matrix) [3x3]"""
        benchmark_names = list(rankings.keys())
        n = len(benchmark_names)

        # Initialize matrices
        corr_matrix = pd.DataFrame(
            np.eye(n),
            index=benchmark_names,
            columns=benchmark_names
        )
        pvalue_matrix = pd.DataFrame(
            np.zeros((n, n)),
            index=benchmark_names,
            columns=benchmark_names
        )

        print("\n[Correlation Analysis] Computing pairwise Spearman correlations:")

        # Compute pairwise correlations
        for i, b1 in enumerate(benchmark_names):
            for j, b2 in enumerate(benchmark_names):
                if i < j:
                    rho, pvalue = self.compute_spearman(rankings[b1], rankings[b2])
                    corr_matrix.loc[b1, b2] = rho
                    corr_matrix.loc[b2, b1] = rho
                    pvalue_matrix.loc[b1, b2] = pvalue
                    pvalue_matrix.loc[b2, b1] = pvalue

                    sig_marker = "***" if pvalue < 0.001 else "**" if pvalue < 0.01 else "*" if pvalue < 0.05 else "ns"
                    print(f"  {b1} vs {b2}: ρ = {rho:.3f}, p = {pvalue:.4f} ({sig_marker})")

        return corr_matrix, pvalue_matrix

    def check_gate_success(
        self, correlations: pd.DataFrame, pvalues: pd.DataFrame,
        target_rho_min: float = 0.3, target_rho_max: float = 0.6
    ) -> Dict[str, Any]:
        """Check ≥2 pairs in [0.3, 0.6], p<0.01. Returns: {passed, success_count, pairs}"""
        success_count = 0
        success_pairs = []
        all_pairs = []

        benchmark_names = list(correlations.index)

        for i, b1 in enumerate(benchmark_names):
            for j, b2 in enumerate(benchmark_names):
                if i < j:
                    rho = correlations.loc[b1, b2]
                    pvalue = pvalues.loc[b1, b2]

                    in_range = target_rho_min <= rho <= target_rho_max
                    significant = pvalue < self.significance_level

                    pair_info = {
                        'pair': f"{b1}-{b2}",
                        'rho': float(rho),
                        'pvalue': float(pvalue),
                        'in_range': in_range,
                        'significant': significant,
                        'meets_gate': in_range and significant
                    }
                    all_pairs.append(pair_info)

                    if in_range and significant:
                        success_count += 1
                        success_pairs.append(f"{b1}-{b2}")

        passed = success_count >= 2

        print(f"\n[Gate Check] Success count: {success_count}/3 pairs in range [{target_rho_min}, {target_rho_max}]")
        print(f"[Gate Check] MUST_WORK gate: {'PASSED' if passed else 'FAILED'}")

        return {
            'passed': passed,
            'success_count': success_count,
            'success_pairs': success_pairs,
            'all_pairs': all_pairs,
            'target_range': (target_rho_min, target_rho_max)
        }

    def check_falsification(
        self, correlations: pd.DataFrame, pvalues: pd.DataFrame,
        scalar_threshold: float = 0.8, random_threshold: float = 0.1
    ) -> Dict[str, Any]:
        """Check ρ>0.8 or ρ<0.1. Returns: {falsified, flags, reason}"""
        flags = []
        reasons = []

        benchmark_names = list(correlations.index)

        # Check for scalar property (ρ > 0.8)
        scalar_pairs = []
        for i, b1 in enumerate(benchmark_names):
            for j, b2 in enumerate(benchmark_names):
                if i < j:
                    rho = correlations.loc[b1, b2]
                    pvalue = pvalues.loc[b1, b2]

                    if rho > scalar_threshold and pvalue < self.significance_level:
                        scalar_pairs.append(f"{b1}-{b2} (ρ={rho:.3f})")

        if scalar_pairs:
            flags.append("scalar_property")
            reasons.append(f"High correlation (ρ > {scalar_threshold}): {', '.join(scalar_pairs)}")

        # Check for random noise (all ρ < 0.1)
        random_pairs = []
        all_random = True
        for i, b1 in enumerate(benchmark_names):
            for j, b2 in enumerate(benchmark_names):
                if i < j:
                    rho = abs(correlations.loc[b1, b2])
                    if rho >= random_threshold:
                        all_random = False
                    else:
                        random_pairs.append(f"{b1}-{b2} (ρ={rho:.3f})")

        if all_random:
            flags.append("random_noise")
            reasons.append(f"All correlations near zero (|ρ| < {random_threshold})")

        # Check for non-significant results
        nonsig_pairs = []
        for i, b1 in enumerate(benchmark_names):
            for j, b2 in enumerate(benchmark_names):
                if i < j:
                    pvalue = pvalues.loc[b1, b2]
                    if pvalue > self.significance_level:
                        nonsig_pairs.append(f"{b1}-{b2} (p={pvalue:.4f})")

        if nonsig_pairs:
            flags.append("not_significant")
            reasons.append(f"Non-significant correlations (p > {self.significance_level}): {', '.join(nonsig_pairs)}")

        falsified = len(flags) > 0

        print(f"\n[Falsification Check] Falsified: {falsified}")
        if flags:
            print(f"[Falsification Check] Flags: {', '.join(flags)}")
            for reason in reasons:
                print(f"  - {reason}")
        else:
            print(f"[Falsification Check] No falsification conditions detected")

        return {
            'falsified': falsified,
            'flags': flags,
            'reasons': reasons
        }
