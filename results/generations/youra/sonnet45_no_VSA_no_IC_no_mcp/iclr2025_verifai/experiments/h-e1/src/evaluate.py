"""Statistical analysis of error mode heterogeneity."""

import numpy as np
from scipy import stats
from typing import Literal, Tuple
import json
from pathlib import Path


class HeterogeneityAnalyzer:
    """Analyze error mode distributions across benchmarks."""

    def __init__(self, classifications: dict[str, list[str]]):
        """
        Args:
            classifications: {benchmark_name: [error_mode per problem]}
        """
        self.classifications = classifications
        self.benchmarks = list(classifications.keys())

    def compute_error_distribution(self, benchmark: str) -> dict[str, float]:
        """
        Compute error mode percentages for one benchmark.
        Returns: {"syntax": 0.25, "type": 0.15, "semantic": 0.40, "pass": 0.20}
        """
        modes = self.classifications[benchmark]
        total = len(modes)

        if total == 0:
            return {}

        counts = {
            "syntax": modes.count("syntax"),
            "type": modes.count("type"),
            "semantic": modes.count("semantic"),
            "pass": modes.count("pass"),
            "uncategorized": modes.count("uncategorized")
        }

        percentages = {
            mode: (count / total) * 100
            for mode, count in counts.items()
        }

        return percentages

    def get_all_distributions(self) -> dict[str, dict[str, float]]:
        """Returns: {benchmark: {error_mode: percentage}}"""
        return {
            bench: self.compute_error_distribution(bench)
            for bench in self.benchmarks
        }

    def compute_cv(self, metric: str = "syntax") -> float:
        """
        Compute coefficient of variation for error mode across benchmarks.
        Formula: std(percentages) / mean(percentages)
        """
        percentages = []
        for bench in self.benchmarks:
            dist = self.compute_error_distribution(bench)
            percentages.append(dist.get(metric, 0.0))

        percentages = np.array(percentages)
        mean = np.mean(percentages)

        if mean == 0:
            return 0.0

        cv = np.std(percentages, ddof=1) / mean
        return cv

    def run_anova(self, metric: str = "syntax") -> Tuple[float, float]:
        """
        One-way ANOVA on error counts across benchmarks.
        H0: Mean syntax% same across all benchmarks
        Returns: (f_statistic, p_value)
        """
        groups = []
        for bench in self.benchmarks:
            modes = self.classifications[bench]
            # Binary encoding: 1 if error mode matches, 0 otherwise
            group = [1 if m == metric else 0 for m in modes]
            groups.append(group)

        f_stat, p_value = stats.f_oneway(*groups)
        return f_stat, p_value

    def pairwise_tests(
        self,
        metric: str = "syntax",
        alpha: float = 0.05
    ) -> dict[Tuple[str, str], dict[str, float]]:
        """
        Pairwise t-tests between all benchmark pairs.
        Returns: {(bench1, bench2): {"t_stat": x, "p_value": y}}
        """
        results = {}

        for i, b1 in enumerate(self.benchmarks):
            for b2 in self.benchmarks[i+1:]:
                modes1 = self.classifications[b1]
                modes2 = self.classifications[b2]

                # Binary encoding
                group1 = [1 if m == metric else 0 for m in modes1]
                group2 = [1 if m == metric else 0 for m in modes2]

                t_stat, p_value = stats.ttest_ind(group1, group2)

                results[(b1, b2)] = {
                    "t_stat": t_stat,
                    "p_value": p_value,
                    "significant": p_value < alpha
                }

        return results

    def gate_decision(
        self,
        cv_threshold: float = 0.3,
        anova_threshold: float = 0.05
    ) -> Tuple[Literal["PASS", "FAIL"], dict]:
        """
        Gate decision logic.
        Returns: (decision, metrics)
        """
        cv = self.compute_cv("syntax")
        anova_f, anova_p = self.run_anova("syntax")

        # Compute uncategorized percentage across all benchmarks
        all_modes = []
        for modes in self.classifications.values():
            all_modes.extend(modes)

        total = len(all_modes)
        uncategorized_count = all_modes.count("uncategorized")
        uncategorized_pct = (uncategorized_count / total) * 100 if total > 0 else 0

        # Max difference from HumanEval (if available)
        max_diff = 0.0
        if "humaneval" in self.benchmarks:
            humaneval_dist = self.compute_error_distribution("humaneval")
            humaneval_syntax = humaneval_dist.get("syntax", 0.0)

            for bench in self.benchmarks:
                if bench != "humaneval":
                    dist = self.compute_error_distribution(bench)
                    syntax_pct = dist.get("syntax", 0.0)
                    diff = abs(syntax_pct - humaneval_syntax)
                    max_diff = max(max_diff, diff)

        metrics = {
            "cv": cv,
            "anova_f": anova_f,
            "anova_p": anova_p,
            "max_diff_from_humaneval": max_diff,
            "uncategorized_pct": uncategorized_pct
        }

        # Gate logic: CV >0.3 AND ANOVA p<0.05 AND uncategorized <10%
        if cv > cv_threshold and anova_p < anova_threshold and uncategorized_pct < 10.0:
            return "PASS", metrics
        else:
            return "FAIL", metrics

    def save_results(self, output_path: str) -> None:
        """Save analysis to JSON."""
        distributions = self.get_all_distributions()
        decision, metrics = self.gate_decision()
        pairwise = self.pairwise_tests()

        # Convert tuple keys to strings for JSON serialization
        pairwise_serializable = {
            f"{k[0]}_vs_{k[1]}": v
            for k, v in pairwise.items()
        }

        data = {
            "benchmarks": {
                bench: {
                    "total_problems": len(self.classifications[bench]),
                    **{
                        f"{mode}_count": self.classifications[bench].count(mode)
                        for mode in ["syntax", "type", "semantic", "pass", "uncategorized"]
                    },
                    **{
                        f"{mode}_pct": distributions[bench].get(mode, 0.0)
                        for mode in ["syntax", "type", "semantic", "pass", "uncategorized"]
                    }
                }
                for bench in self.benchmarks
            },
            "analysis": {
                **metrics,
                "gate_decision": decision
            },
            "pairwise_tests": pairwise_serializable
        }

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

        print(f"Saved analysis to {output_path}")
