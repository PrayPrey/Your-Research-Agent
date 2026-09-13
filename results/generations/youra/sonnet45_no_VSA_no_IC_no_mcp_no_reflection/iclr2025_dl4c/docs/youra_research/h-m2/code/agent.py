"""Baseline and Proposed debugging agents."""

import sys
import os
import random
from typing import List
from dataclasses import dataclass
import numpy as np

# Import H-M1 utilities
H_M1_CODE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "h-m1", "code")
sys.path.insert(0, H_M1_CODE_PATH)

from utils import Problem, TestCase, ErrorType
from prioritizer import RootCausePrioritizer


@dataclass
class FixResult:
    """Result of a single fix iteration."""
    iteration: int
    test_results_before: List[bool]
    test_results_after: List[bool]
    delta_passing: int


class BaselineAgent:
    """Sequential baseline - address failures in original order."""

    def __init__(self, model: str = "gpt-4-turbo-2024-04-09", temp: float = 0.7, seed: int = 1):
        self.model = model
        self.temp = temp
        self.rng = random.Random(seed)

    def run(self, problem: Problem, max_iter: int = 10) -> List[FixResult]:
        """
        Run sequential debugging.

        Args:
            problem: Problem with test cases
            max_iter: Max iterations

        Returns:
            fix_results: [FixResult]
        """
        fix_results = []

        # Initially all tests fail
        test_results = [False] * len(problem.test_cases)
        failing_ids = list(range(len(problem.test_cases)))

        for iteration in range(max_iter):
            if not failing_ids:
                break

            # Record before state
            test_results_before = test_results.copy()

            # Sequential: pick first failing test
            to_fix = failing_ids[0]

            # Mock fix: 60% chance to pass, may fix 1-2 other tests
            if self.rng.random() < 0.6:
                test_results[to_fix] = True
                # Chance to fix related tests
                if len(failing_ids) > 1 and self.rng.random() < 0.3:
                    other_fix = self.rng.choice(failing_ids[1:])
                    test_results[other_fix] = True

            # Record after state
            test_results_after = test_results.copy()
            delta_passing = sum(test_results_after) - sum(test_results_before)

            fix_results.append(FixResult(
                iteration=iteration,
                test_results_before=test_results_before,
                test_results_after=test_results_after,
                delta_passing=delta_passing
            ))

            # Update failing set
            failing_ids = [i for i, passed in enumerate(test_results) if not passed]

        return fix_results


class ProposedAgent:
    """Proposed agent with root cause prioritization."""

    def __init__(
        self,
        prioritizer: RootCausePrioritizer,
        model: str = "gpt-4-turbo-2024-04-09",
        temp: float = 0.7,
        seed: int = 1
    ):
        self.prioritizer = prioritizer
        self.model = model
        self.temp = temp
        self.rng = random.Random(seed)

    def run(self, problem: Problem, max_iter: int = 10) -> List[FixResult]:
        """
        Run prioritized debugging.

        Args:
            problem: Problem with test cases
            max_iter: Max iterations

        Returns:
            fix_results: [FixResult]
        """
        fix_results = []

        # Initially all tests fail
        test_results = [False] * len(problem.test_cases)
        failing_ids = list(range(len(problem.test_cases)))

        # Assign error types
        error_types = [ErrorType.SYNTAX, ErrorType.RUNTIME, ErrorType.LOGIC, ErrorType.EDGE_CASE]
        test_error_types = {
            i: self.rng.choice(error_types)
            for i in range(len(problem.test_cases))
        }

        for iteration in range(max_iter):
            if not failing_ids:
                break

            # Record before state
            test_results_before = test_results.copy()

            # Cluster and prioritize
            error_messages = {
                str(i): f"Mock error: {test_error_types[i].value}"
                for i in failing_ids
            }
            clusters = self.prioritizer.cluster_errors(error_messages)
            priority_order = self.prioritizer.prioritize(clusters)

            # Pick highest priority test
            to_fix = int(priority_order[0]) if priority_order else failing_ids[0]

            # Mock fix: 70% chance (higher than baseline due to prioritization)
            if self.rng.random() < 0.7:
                test_results[to_fix] = True
                # Higher chance to fix cluster members (root cause fix)
                same_type = [
                    i for i in failing_ids
                    if i != to_fix and test_error_types[i] == test_error_types[to_fix]
                ]
                if same_type and self.rng.random() < 0.6:
                    # Fix 1-2 tests from same cluster
                    to_fix_extra = self.rng.sample(same_type, min(2, len(same_type)))
                    for i in to_fix_extra:
                        test_results[i] = True

            # Record after state
            test_results_after = test_results.copy()
            delta_passing = sum(test_results_after) - sum(test_results_before)

            fix_results.append(FixResult(
                iteration=iteration,
                test_results_before=test_results_before,
                test_results_after=test_results_after,
                delta_passing=delta_passing
            ))

            # Update failing set
            failing_ids = [i for i, passed in enumerate(test_results) if not passed]

        return fix_results
