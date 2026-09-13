"""
E1-3: Statistical Analysis Module - StatisticalAnalyzer
Implements power analysis and coverage metrics.
"""

import pandas as pd
import numpy as np
from scipy.stats import norm
from typing import Dict


class StatisticalAnalyzer:
    """
    Statistical power analysis and coverage validation.

    Features:
    - Cohen's d power analysis for two-sample t-test
    - Domain coverage analysis (CV, NLP distribution)
    - Reproduction depth metrics (median, mean, std)
    """

    def __init__(self, effect_size: float = 0.57, alpha: float = 0.05, power: float = 0.80):
        """
        Initialize analyzer.

        Args:
            effect_size: Cohen's d (default: 0.57 = medium effect)
            alpha: Significance level (two-tailed)
            power: Statistical power (1 - beta)
        """
        self.effect_size = effect_size
        self.alpha = alpha
        self.power = power

    def calculate_required_n(self) -> int:
        """
        Calculate required sample size for two-sample t-test.

        Formula: N = 2 * ((z_alpha + z_beta) / d)^2

        Returns:
            Required total sample size (both groups)
        """
        z_alpha = norm.ppf(1 - self.alpha / 2)  # Two-tailed
        z_beta = norm.ppf(self.power)

        n_per_group = ((z_alpha + z_beta) / self.effect_size) ** 2
        total_n = 2 * n_per_group

        return int(np.ceil(total_n))

    def check_power_sufficiency(self, actual_n: int) -> Dict:
        """
        Check if sample size supports desired power.

        Args:
            actual_n: Actual total sample size

        Returns:
            Power analysis result dict
        """
        required_n = self.calculate_required_n()
        sufficient = actual_n >= required_n

        result = {
            'required_n': required_n,
            'actual_n': actual_n,
            'power_sufficient': sufficient,
            'effect_size': self.effect_size,
            'alpha': self.alpha,
            'power': self.power
        }

        print(f"\n📊 Power Analysis:")
        print(f"  Effect size (Cohen's d): {self.effect_size}")
        print(f"  Required N (80% power): {required_n}")
        print(f"  Actual N: {actual_n}")
        print(f"  Power sufficient: {'✅ Yes' if sufficient else '❌ No'}")

        return result

    def analyze_domain_coverage(self, df: pd.DataFrame) -> Dict:
        """
        Analyze distribution across ML domains.

        Args:
            df: Benchmark DataFrame with 'task' column

        Returns:
            Domain coverage result dict
        """
        if 'task' not in df.columns:
            return {
                'domain_count': 0,
                'distribution': {},
                'error': 'No task column in DataFrame'
            }

        domain_counts = df['task'].value_counts().to_dict()
        n_domains = len(domain_counts)

        result = {
            'domain_count': n_domains,
            'distribution': domain_counts,
            'sufficient_coverage': n_domains >= 2
        }

        print(f"\n🌐 Domain Coverage:")
        print(f"  Unique domains: {n_domains}")
        for domain, count in list(domain_counts.items())[:5]:
            print(f"    {domain}: {count}")

        return result

    def analyze_reproduction_depth(self, df: pd.DataFrame) -> Dict:
        """
        Analyze reproduction attempt distribution.

        Args:
            df: Benchmark DataFrame with 'result_count' column

        Returns:
            Reproduction depth result dict
        """
        if 'result_count' not in df.columns:
            return {
                'error': 'No result_count column in DataFrame'
            }

        result_counts = df['result_count']

        result = {
            'median': int(result_counts.median()),
            'mean': float(result_counts.mean()),
            'std': float(result_counts.std()),
            'min': int(result_counts.min()),
            'max': int(result_counts.max())
        }

        print(f"\n📈 Reproduction Depth:")
        print(f"  Median: {result['median']}")
        print(f"  Mean: {result['mean']:.2f}")
        print(f"  Std: {result['std']:.2f}")
        print(f"  Range: [{result['min']}, {result['max']}]")

        return result
