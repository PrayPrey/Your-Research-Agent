"""Statistical Analysis Module - Hypothesis testing for information gradient"""

from typing import Dict, List
from dataclasses import dataclass
import numpy as np
from scipy.stats import linregress

from .feedback_ablator import FeedbackCondition
from .ablation_experiment import AblationResults


@dataclass
class MonotonicTest:
    """Test if conditions are monotonically ordered"""
    passed: bool
    ordering: List[str]
    expected: List[str]
    violations: List[str]


@dataclass
class GapTest:
    """Test if adjacent gaps ≥ threshold"""
    passed: bool
    gaps: Dict[str, float]
    threshold: float
    failed_gaps: List[str]


@dataclass
class RegressionResult:
    """Linear regression: feedback richness -> discharge rate"""
    coefficient: float
    p_value: float
    r_squared: float
    significant: bool


@dataclass
class GateDecision:
    """Final hypothesis validation decision"""
    status: str  # SATISFIED | FAILED
    passing_tests: List[str]
    failing_tests: List[str]
    reason: str


class StatisticalAnalyzer:
    """Hypothesis testing for information gradient"""

    def __init__(self, significance_level: float = 0.05):
        self.alpha = significance_level

    def test_monotonic_ordering(
        self,
        condition_means: Dict[str, float]
    ) -> MonotonicTest:
        """
        Check: FullStructured > ObligationSlice > TagOnly > RawError.

        Args:
            condition_means: {condition -> mean discharge rate}

        Returns:
            MonotonicTest result
        """
        expected = [
            FeedbackCondition.RAW_ERROR.value,
            FeedbackCondition.TAG_ONLY.value,
            FeedbackCondition.OBLIGATION_SLICE.value,
            FeedbackCondition.FULL_STRUCTURED.value
        ]

        actual = sorted(condition_means.keys(), key=lambda c: condition_means[c])

        passed = (actual == expected)
        violations = [f"{actual[i]} vs {expected[i]}"
                     for i in range(len(expected)) if actual[i] != expected[i]]

        return MonotonicTest(
            passed=passed,
            ordering=actual,
            expected=expected,
            violations=violations
        )

    def test_adjacent_gaps(
        self,
        condition_means: Dict[str, float],
        threshold: float = 10.0
    ) -> GapTest:
        """
        Check: Each adjacent gap ≥ 10 percentage points.

        Args:
            condition_means: {condition -> mean discharge rate}
            threshold: Minimum gap in pp (default: 10.0)

        Returns:
            GapTest result
        """
        expected_order = [
            FeedbackCondition.RAW_ERROR.value,
            FeedbackCondition.TAG_ONLY.value,
            FeedbackCondition.OBLIGATION_SLICE.value,
            FeedbackCondition.FULL_STRUCTURED.value
        ]

        gaps = {}
        failed_gaps = []

        for i in range(len(expected_order) - 1):
            lower = expected_order[i]
            upper = expected_order[i + 1]
            gap = condition_means[upper] - condition_means[lower]
            gap_name = f"{upper} - {lower}"
            gaps[gap_name] = gap

            if gap < threshold:
                failed_gaps.append(gap_name)

        return GapTest(
            passed=(len(failed_gaps) == 0),
            gaps=gaps,
            threshold=threshold,
            failed_gaps=failed_gaps
        )

    def run_regression(
        self,
        ablation_results: AblationResults
    ) -> RegressionResult:
        """
        Linear regression: ordinal feedback -> discharge rate.

        Encoding:
            RawError -> 1
            TagOnly -> 2
            ObligationSlice -> 3
            FullStructured -> 4

        Test: β > 0, p < 0.05

        Args:
            ablation_results: All trial results

        Returns:
            RegressionResult with coefficient and significance
        """
        encoding = {
            FeedbackCondition.RAW_ERROR.value: 1,
            FeedbackCondition.TAG_ONLY.value: 2,
            FeedbackCondition.OBLIGATION_SLICE.value: 3,
            FeedbackCondition.FULL_STRUCTURED.value: 4
        }

        x = []
        y = []

        for trial in ablation_results.raw_trials:
            x.append(encoding[trial.condition])
            y.append(trial.discharge_rate)

        slope, intercept, r_value, p_value, std_err = linregress(x, y)

        return RegressionResult(
            coefficient=slope,
            p_value=p_value,
            r_squared=r_value ** 2,
            significant=(p_value < self.alpha and slope > 0)
        )

    def make_gate_decision(
        self,
        monotonic: MonotonicTest,
        gaps: GapTest,
        regression: RegressionResult
    ) -> GateDecision:
        """
        Combine all tests for final gate decision.

        SATISFIED: All 3 tests pass
        FAILED: Any test fails

        Args:
            monotonic: Ordering test result
            gaps: Gap test result
            regression: Regression test result

        Returns:
            GateDecision with status and reason
        """
        passing = []
        failing = []

        if monotonic.passed:
            passing.append("monotonic_ordering")
        else:
            failing.append("monotonic_ordering")

        if gaps.passed:
            passing.append("adjacent_gaps")
        else:
            failing.append("adjacent_gaps")

        if regression.significant:
            passing.append("regression_significance")
        else:
            failing.append("regression_significance")

        if len(failing) == 0:
            status = "SATISFIED"
            reason = "All 3 hypothesis tests passed: information gradient confirmed"
        else:
            status = "FAILED"
            reason = f"Failed tests: {', '.join(failing)}"

        return GateDecision(
            status=status,
            passing_tests=passing,
            failing_tests=failing,
            reason=reason
        )
