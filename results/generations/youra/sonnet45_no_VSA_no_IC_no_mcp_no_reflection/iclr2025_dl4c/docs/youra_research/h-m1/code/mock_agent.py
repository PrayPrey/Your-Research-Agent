"""Mock debugging agent for PoC without OpenAI API."""

import random
from typing import List
from utils import Problem, TestCase, DebugSession, DebugIteration, TestFailure, ErrorType


class MockDebugAgent:
    """Mock agent that simulates error clustering behavior."""

    def __init__(self, seed: int = 1, clustering_strength: float = 0.4):
        """
        Args:
            seed: Random seed
            clustering_strength: How much agent clusters errors (0.0 = random, 1.0 = perfect)
        """
        self.rng = random.Random(seed)
        self.clustering_strength = clustering_strength

    def run_debug_session(self, problem: Problem, max_iterations: int = 10) -> DebugSession:
        """Simulate debugging session with controlled clustering."""

        iterations = []
        fix_sequence = []
        failures = []

        # Assign error types to test cases (use unique IDs: problem_id + case_id)
        error_types = [ErrorType.SYNTAX, ErrorType.RUNTIME, ErrorType.LOGIC, ErrorType.EDGE_CASE]
        test_error_types = {
            f"{problem.problem_id}_test_{tc.case_id}": self.rng.choice(error_types)
            for tc in problem.test_cases
        }

        # Map original case IDs to unique IDs
        unique_id_map = {
            tc.case_id: f"{problem.problem_id}_test_{tc.case_id}"
            for tc in problem.test_cases
        }

        # Initially all tests fail
        failing_ids = [tc.case_id for tc in problem.test_cases]
        passing_count = 0

        for iteration_num in range(max_iterations):
            if not failing_ids:
                break

            # Record iteration state
            iterations.append(DebugIteration(
                iteration=iteration_num,
                code=f"# iteration {iteration_num}",
                passing_count=passing_count,
                failing_test_ids=failing_ids.copy()
            ))

            # Choose which tests to fix this iteration (use unique IDs)
            if self.clustering_strength > 0 and iteration_num > 0:
                # Group by error type, pick one type cluster
                by_type = {}
                for tid in failing_ids:
                    unique_id = unique_id_map[tid]
                    et = test_error_types[unique_id]
                    by_type.setdefault(et, []).append(tid)

                # With clustering_strength probability, pick a whole type cluster
                if self.rng.random() < self.clustering_strength and by_type:
                    type_to_fix = self.rng.choice(list(by_type.keys()))
                    to_fix = by_type[type_to_fix][:3]  # Fix up to 3 from same type
                else:
                    to_fix = self.rng.sample(failing_ids, min(2, len(failing_ids)))
            else:
                # Random fixes
                to_fix = self.rng.sample(failing_ids, min(2, len(failing_ids)))

            # Fix tests (record with unique IDs)
            for tid in to_fix:
                unique_id = unique_id_map[tid]
                fix_sequence.append(unique_id)
                failures.append(TestFailure(
                    test_id=unique_id,
                    iteration=iteration_num,
                    error_msg=f"Mock error: {test_error_types[unique_id].value}",
                    input_data=f"input_{tid}",
                    expected=f"output_{tid}",
                    actual=f"actual_{tid}",
                    error_type=test_error_types[unique_id]
                ))

            # Update state
            for tid in to_fix:
                if tid in failing_ids:
                    failing_ids.remove(tid)
            passing_count += len(to_fix)

        return DebugSession(
            problem_id=problem.problem_id,
            iterations=iterations,
            fix_sequence=fix_sequence,
            failures=failures
        )


def generate_mock_problems(count: int = 50, min_tests: int = 15, seed: int = 1) -> List[Problem]:
    """Generate mock Codeforces problems."""
    rng = random.Random(seed)

    problems = []
    for i in range(count):
        num_tests = rng.randint(min_tests, 25)
        test_cases = [
            TestCase(
                case_id=j,
                input_data=f"input_{j}",
                expected_output=f"output_{j}"
            )
            for j in range(num_tests)
        ]

        problems.append(Problem(
            problem_id=f"mock_problem_{i}",
            title=f"Mock Problem {i}",
            rating=rng.randint(1200, 1800),
            solve_count=rng.randint(1000, 5000),
            test_cases=test_cases
        ))

    return problems
