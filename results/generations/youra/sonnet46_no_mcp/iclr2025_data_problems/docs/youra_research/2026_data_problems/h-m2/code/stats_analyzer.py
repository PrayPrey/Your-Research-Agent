from __future__ import annotations

import math
from typing import TYPE_CHECKING

import numpy as np
from scipy import stats

if TYPE_CHECKING:
    from config import Config


class StatsAnalyzer:
    """Statistical analysis for H-M2 domain-stratified contamination."""

    def __init__(self, config: "Config"):
        self.config = config

    def compute_domain_stratified_rates(
        self,
        matrix: dict,
        domain_map: dict[str, str],
    ) -> dict:
        """Returns {corpus: {domain: mean_rate, domain+'_rates': list[float]}} for 2x3 table."""
        result = {}
        for corpus in self.config.corpora:
            academic_rates = [
                matrix[t][corpus] for t in matrix if domain_map.get(t) == "academic"
            ]
            commonsense_rates = [
                matrix[t][corpus] for t in matrix if domain_map.get(t) == "commonsense"
            ]
            result[corpus] = {
                "academic": float(np.mean(academic_rates)) if academic_rates else 0.0,
                "academic_rates": academic_rates,
                "commonsense": float(np.mean(commonsense_rates)) if commonsense_rates else 0.0,
                "commonsense_rates": commonsense_rates,
            }
        return result

    def mann_whitney_directional(
        self,
        group_a: list[float],
        group_b: list[float],
        alternative: str = "greater",
    ) -> dict:
        """One-tailed Mann-Whitney U test: group_a {alternative} group_b."""
        stat, p = stats.mannwhitneyu(group_a, group_b, alternative=alternative)
        n1, n2 = len(group_a), len(group_b)
        effect_size_r = 1.0 - (2.0 * stat) / (n1 * n2) if n1 * n2 > 0 else 0.0
        direction_confirmed = bool(p < self.config.alpha)
        return {
            "stat": float(stat),
            "p": float(p),
            "effect_size_r": float(effect_size_r),
            "direction_confirmed": direction_confirmed,
        }

    def cohens_d(self, group_a: list[float], group_b: list[float]) -> float:
        """Cohen's d = (mean_a - mean_b) / pooled_std."""
        n1, n2 = len(group_a), len(group_b)
        if n1 < 2 or n2 < 2:
            return 0.0
        mean_diff = float(np.mean(group_a)) - float(np.mean(group_b))
        var_a = float(np.var(group_a, ddof=1))
        var_b = float(np.var(group_b, ddof=1))
        pooled_var = ((n1 - 1) * var_a + (n2 - 1) * var_b) / (n1 + n2 - 2)
        pooled_std = math.sqrt(pooled_var) if pooled_var > 0 else 0.0
        return mean_diff / pooled_std if pooled_std > 0 else 0.0

    def run_directional_tests(self, stratified: dict) -> dict:
        """Runs directional tests for all 3 corpora per config.directional_predictions."""
        tests = {}

        # Pile: academic > commonsense
        a_rates = stratified["pile"]["academic_rates"]
        c_rates = stratified["pile"]["commonsense_rates"]
        res = self.mann_whitney_directional(a_rates, c_rates, "greater")
        res["cohens_d"] = self.cohens_d(a_rates, c_rates)
        tests["pile_academic_gt_commonsense"] = res

        # C4: commonsense > academic (swap groups)
        a_rates = stratified["c4"]["academic_rates"]
        c_rates = stratified["c4"]["commonsense_rates"]
        res = self.mann_whitney_directional(c_rates, a_rates, "greater")
        res["cohens_d"] = self.cohens_d(c_rates, a_rates)
        tests["c4_commonsense_gt_academic"] = res

        # RedPajama: academic > commonsense (exploratory)
        a_rates = stratified["redpajama"]["academic_rates"]
        c_rates = stratified["redpajama"]["commonsense_rates"]
        res = self.mann_whitney_directional(a_rates, c_rates, "greater")
        res["cohens_d"] = self.cohens_d(a_rates, c_rates)
        tests["redpajama_academic_gt_commonsense"] = res

        return tests

    def kruskal_interaction(self, stratified: dict) -> dict:
        """Kruskal-Wallis across all 6 (corpus x domain) groups."""
        groups = []
        for corpus in self.config.corpora:
            groups.append(stratified[corpus]["academic_rates"])
            groups.append(stratified[corpus]["commonsense_rates"])
        H, p = stats.kruskal(*groups)
        return {
            "H": float(H),
            "p": float(p),
            "significant": bool(p < self.config.alpha),
        }

    def top_n_per_corpus(
        self,
        matrix: dict,
        domain_map: dict[str, str],
        n: int = 5,
    ) -> dict:
        """Returns {corpus: [{subtask, rate, domain}]} sorted descending."""
        result = {}
        for corpus in self.config.corpora:
            items = [
                {
                    "subtask": t,
                    "rate": matrix[t][corpus],
                    "domain": domain_map.get(t, "academic"),
                }
                for t in matrix
            ]
            items.sort(key=lambda x: x["rate"], reverse=True)
            result[corpus] = items[:n]
        return result

    def assert_gate(self, directional_tests: dict) -> bool:
        """Returns True if >=2 corpora have direction_confirmed=True."""
        confirmed = sum(
            1 for t in directional_tests.values() if t["direction_confirmed"]
        )
        return confirmed >= self.config.min_corpora_directional_confirmed
