"""Statistical analysis for compute-matched control hypothesis."""

import numpy as np
from scipy import stats
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class HypothesisTestResult:
    """Results from hypothesis test."""
    mean_baseline1: float
    mean_baseline2: float
    mean_difference: float
    t_statistic: float
    p_value: float
    cohens_d: float
    gate_satisfied: bool


@dataclass
class ComputeFairnessResult:
    """Compute budget fairness validation."""
    baseline1_avg_tokens: float
    baseline2_avg_tokens: float
    token_ratio: float
    token_budget_fair: bool
    baseline1_avg_time: float
    baseline2_avg_time: float
    time_ratio: float
    time_budget_fair: bool
    overall_fair: bool


@dataclass
class GateDecision:
    """Final gate decision."""
    status: str  # SATISFIED | FAILED
    criteria: Dict[str, bool]
    failure_reasons: List[str]


class StatisticalAnalyzer:
    """Performs statistical analysis for h-c1 gate decision."""

    def __init__(self, significance_level: float = 0.05):
        self.significance_level = significance_level

    def primary_hypothesis_test(self, baseline1_rates: List[float], baseline2_rates: List[float]) -> HypothesisTestResult:
        """Test if iterative feedback > self-consistency by ≥10pp."""
        baseline1_arr = np.array(baseline1_rates)
        baseline2_arr = np.array(baseline2_rates)

        # Paired t-test
        t_stat, p_value = stats.ttest_rel(baseline1_arr, baseline2_arr)

        # Mean difference
        mean_b1 = np.mean(baseline1_arr)
        mean_b2 = np.mean(baseline2_arr)
        mean_diff = mean_b1 - mean_b2

        # Cohen's d for paired samples
        differences = baseline1_arr - baseline2_arr
        std_diff = np.std(differences, ddof=1)
        cohens_d = mean_diff / std_diff if std_diff > 0 else 0.0

        # Gate criteria
        gate_satisfied = (
            mean_diff >= 10.0 and
            p_value < self.significance_level and
            cohens_d >= 0.5
        )

        return HypothesisTestResult(
            mean_baseline1=mean_b1,
            mean_baseline2=mean_b2,
            mean_difference=mean_diff,
            t_statistic=t_stat,
            p_value=p_value,
            cohens_d=cohens_d,
            gate_satisfied=gate_satisfied
        )

    def validate_compute_fairness(
        self,
        baseline1_budgets: List[Dict],
        baseline2_budgets: List[Dict],
        tolerance: float = 0.10
    ) -> ComputeFairnessResult:
        """Validate compute budgets are matched within tolerance."""
        b1_tokens = np.mean([b['total_tokens'] for b in baseline1_budgets])
        b2_tokens = np.mean([b['total_tokens'] for b in baseline2_budgets])
        token_ratio = b2_tokens / b1_tokens if b1_tokens > 0 else 1.0

        b1_time = np.mean([b['verifier_time_seconds'] for b in baseline1_budgets])
        b2_time = np.mean([b['verifier_time_seconds'] for b in baseline2_budgets])
        time_ratio = b2_time / b1_time if b1_time > 0 else 1.0

        token_fair = (1.0 - tolerance) <= token_ratio <= (1.0 + tolerance)
        time_fair = (1.0 - tolerance) <= time_ratio <= (1.0 + tolerance)

        return ComputeFairnessResult(
            baseline1_avg_tokens=b1_tokens,
            baseline2_avg_tokens=b2_tokens,
            token_ratio=token_ratio,
            token_budget_fair=token_fair,
            baseline1_avg_time=b1_time,
            baseline2_avg_time=b2_time,
            time_ratio=time_ratio,
            time_budget_fair=time_fair,
            overall_fair=(token_fair and time_fair)
        )

    def make_gate_decision(
        self,
        hypothesis_test: HypothesisTestResult,
        fairness: ComputeFairnessResult
    ) -> GateDecision:
        """Make final gate decision based on all criteria."""
        criteria = {
            'mean_difference_10pp': hypothesis_test.mean_difference >= 10.0,
            'statistical_significance': hypothesis_test.p_value < self.significance_level,
            'medium_effect_size': hypothesis_test.cohens_d >= 0.5,
            'compute_budget_fair': fairness.overall_fair
        }

        gate_satisfied = all(criteria.values())
        failure_reasons = [k for k, v in criteria.items() if not v]

        return GateDecision(
            status='SATISFIED' if gate_satisfied else 'FAILED',
            criteria=criteria,
            failure_reasons=failure_reasons
        )
