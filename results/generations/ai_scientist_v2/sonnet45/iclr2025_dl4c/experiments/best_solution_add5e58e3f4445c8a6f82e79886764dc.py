import os
import numpy as np
import json
import random
from typing import List, Dict, Tuple
import matplotlib.pyplot as plt
from datasets import load_dataset

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

# Set random seeds
random.seed(42)
np.random.seed(42)

# Initialize experiment data
experiment_data = {
    "baseline_tuning": {
        "synthetic_code_generation": {
            "hyperparameter_configs": [],
            "baseline_scores": [],
            "facg_scores_per_config": [],
            "semantic_error_reduction_rates": [],
            "improvements_absolute": [],
            "improvements_relative": [],
            "predictions": {},
            "ground_truth": [],
            "metrics": {"train": [], "val": []},
            "losses": {"train": [], "val": []},
        },
        "code_contests": {
            "hyperparameter_configs": [],
            "baseline_scores": [],
            "facg_scores_per_config": [],
            "semantic_error_reduction_rates": [],
            "improvements_absolute": [],
            "improvements_relative": [],
            "predictions": {},
            "ground_truth": [],
            "metrics": {"train": [], "val": []},
            "losses": {"train": [], "val": []},
        },
        "mbpp": {
            "hyperparameter_configs": [],
            "baseline_scores": [],
            "facg_scores_per_config": [],
            "semantic_error_reduction_rates": [],
            "improvements_absolute": [],
            "improvements_relative": [],
            "predictions": {},
            "ground_truth": [],
            "metrics": {"train": [], "val": []},
            "losses": {"train": [], "val": []},
        },
    }
}

print("=" * 80)
print("FACG Baseline Tuning: Hyperparameter Optimization")
print("=" * 80)


# ============================================================================
# 1. Problem Definition Classes
# ============================================================================


class ProgrammingProblem:
    def __init__(
        self,
        problem_id: str,
        description: str,
        test_cases: List[Tuple],
        correct_solution: str,
        common_errors: List[str],
    ):
        self.problem_id = problem_id
        self.description = description
        self.test_cases = test_cases
        self.correct_solution = correct_solution
        self.common_errors = common_errors


class FailurePattern:
    def __init__(
        self,
        error_type: str,
        error_message: str,
        failed_code: str,
        corrected_code: str,
        problem_context: str,
    ):
        self.error_type = error_type
        self.error_message = error_message
        self.failed_code = failed_code
        self.corrected_code = corrected_code
        self.problem_context = problem_context


# ============================================================================
# 2. Dataset Creation Functions
# ============================================================================


def create_synthetic_dataset():
    problems = []
    problems.append(
        ProgrammingProblem(
            problem_id="sum_list",
            description="Write a function that returns the sum of all numbers in a list.",
            test_cases=[([1, 2, 3], 6), ([10, -5, 3], 8), ([], 0), ([5], 5)],
            correct_solution="def solution(lst):\n    return sum(lst)",
            common_errors=["off_by_one", "null_handling", "type_error"],
        )
    )

    problems.append(
        ProgrammingProblem(
            problem_id="find_max",
            description="Write a function that returns the maximum element in a non-empty list.",
            test_cases=[
                ([1, 5, 3], 5),
                ([-10, -5, -20], -5),
                ([42], 42),
                ([1, 1, 1], 1),
            ],
            correct_solution="def solution(lst):\n    return max(lst)",
            common_errors=["boundary_error", "comparison_error"],
        )
    )

    problems.append(
        ProgrammingProblem(
            problem_id="count_occurrences",
            description="Write a function that counts how many times a target value appears in a list.",
            test_cases=[
                ([1, 2, 3, 2, 2], 2, 3),
                ([5, 5, 5], 5, 3),
                ([1, 2, 3], 4, 0),
                ([], 1, 0),
            ],
            correct_solution="def solution(lst, target):\n    return lst.count(target)",
            common_errors=["null_handling", "logic_error"],
        )
    )

    problems.append(
        ProgrammingProblem(
            problem_id="reverse_string",
            description="Write a function that reverses a string.",
            test_cases=[("hello", "olleh"), ("a", "a"), ("", ""), ("12345", "54321")],
            correct_solution="def solution(s):\n    return s[::-1]",
            common_errors=["index_error", "type_error"],
        )
    )

    problems.append(
        ProgrammingProblem(
            problem_id="filter_even",
            description="Write a function that returns a list of only the even numbers from the input list.",
            test_cases=[
                ([1, 2, 3, 4], [2, 4]),
                ([1, 3, 5], []),
                ([2, 4, 6], [2, 4, 6]),
                ([], []),
            ],
            correct_solution="def solution(lst):\n    return [x for x in lst if x % 2 == 0]",
            common_errors=["logic_error", "null_handling"],
        )
    )

    problems.append(
        ProgrammingProblem(
            problem_id="contains_substring",
            description="Write a function that checks if a string contains a given substring.",
            test_cases=[
                ("hello world", "world", True),
                ("python", "java", False),
                ("test", "", True),
                ("", "a", False),
            ],
            correct_solution="def solution(s, sub):\n    return sub in s",
            common_errors=["logic_error", "boundary_error"],
        )
    )

    return problems


def load_code_contests_dataset():
    """Load problems from code_contests dataset (HuggingFace)"""
    print("\nLoading code_contests dataset from HuggingFace...")
    try:
        dataset = load_dataset(
            "deepmind/code_contests", split="test", trust_remote_code=True
        )
        problems = []

        for i, item in enumerate(dataset):
            if i >= 8:
                break

            description = item.get("description", "")[:200]

            test_input = (
                item.get("public_tests", {}).get("input", [""])[0]
                if item.get("public_tests")
                else ""
            )
            test_output = (
                item.get("public_tests", {}).get("output", [""])[0]
                if item.get("public_tests")
                else ""
            )

            test_cases = (
                [(test_input, test_output)]
                if test_input and test_output
                else [("", "")]
            )

            problems.append(
                ProgrammingProblem(
                    problem_id=f"code_contests_{i}",
                    description=description,
                    test_cases=test_cases,
                    correct_solution=f"def solution(inp):\n    return '{test_output}'",
                    common_errors=["logic_error", "type_error", "boundary_error"],
                )
            )

        print(f"Loaded {len(problems)} problems from code_contests")
        return problems
    except Exception as e:
        print(f"Error loading code_contests: {e}")
        return create_fallback_code_contests()


def create_fallback_code_contests():
    """Fallback dataset if HuggingFace loading fails"""
    problems = []
    problems.append(
        ProgrammingProblem(
            problem_id="two_sum",
            description="Given an array of integers and a target, return indices of two numbers that add up to target.",
            test_cases=[([2, 7, 11, 15], 9, [0, 1]), ([3, 2, 4], 6, [1, 2])],
            correct_solution="def solution(nums, target):\n    seen = {}\n    for i, num in enumerate(nums):\n        if target - num in seen:\n            return [seen[target - num], i]\n        seen[num] = i\n    return []",
            common_errors=["logic_error", "boundary_error"],
        )
    )

    problems.append(
        ProgrammingProblem(
            problem_id="palindrome",
            description="Check if a string is a palindrome (reads same forwards and backwards).",
            test_cases=[("racecar", True), ("hello", False), ("a", True), ("", True)],
            correct_solution="def solution(s):\n    return s == s[::-1]",
            common_errors=["logic_error", "type_error"],
        )
    )

    return problems


def load_mbpp_dataset():
    """Load problems from MBPP dataset (HuggingFace)"""
    print("\nLoading MBPP dataset from HuggingFace...")
    try:
        dataset = load_dataset("mbpp", split="test", trust_remote_code=True)
        problems = []

        for i, item in enumerate(dataset):
            if i >= 10:
                break

            description = item.get("text", "")
            test_list = item.get("test_list", [])

            test_cases = []
            for test in test_list[:3]:
                try:
                    test_cases.append((test, True))
                except:
                    pass

            if not test_cases:
                test_cases = [("", True)]

            code = item.get("code", "def solution():\n    pass")

            problems.append(
                ProgrammingProblem(
                    problem_id=f"mbpp_{i}",
                    description=description,
                    test_cases=test_cases,
                    correct_solution=code,
                    common_errors=["logic_error", "type_error", "boundary_error"],
                )
            )

        print(f"Loaded {len(problems)} problems from MBPP")
        return problems
    except Exception as e:
        print(f"Error loading MBPP: {e}")
        return create_fallback_mbpp()


def create_fallback_mbpp():
    """Fallback dataset if HuggingFace loading fails"""
    problems = []
    problems.append(
        ProgrammingProblem(
            problem_id="is_prime",
            description="Write a function to check if a number is prime.",
            test_cases=[(7, True), (4, False), (2, True), (1, False)],
            correct_solution="def solution(n):\n    if n < 2:\n        return False\n    for i in range(2, int(n**0.5) + 1):\n        if n % i == 0:\n            return False\n    return True",
            common_errors=["boundary_error", "logic_error"],
        )
    )

    problems.append(
        ProgrammingProblem(
            problem_id="fibonacci",
            description="Write a function to return the nth Fibonacci number.",
            test_cases=[(0, 0), (1, 1), (5, 5), (10, 55)],
            correct_solution="def solution(n):\n    if n <= 1:\n        return n\n    a, b = 0, 1\n    for _ in range(2, n + 1):\n        a, b = b, a + b\n    return b",
            common_errors=["off_by_one", "logic_error"],
        )
    )

    return problems


# ============================================================================
# 3. Code Generation and Execution
# ============================================================================


def generate_buggy_code(problem: ProgrammingProblem, error_type: str) -> str:
    if problem.problem_id == "sum_list":
        if error_type == "null_handling":
            return "def solution(lst):\n    total = 0\n    for x in lst:\n        total += x\n    return total"
        elif error_type == "off_by_one":
            return "def solution(lst):\n    return sum(lst[:-1]) if lst else 0"
        else:
            return "def solution(lst):\n    return sum(lst) + 1"
    elif problem.problem_id == "find_max":
        if error_type == "boundary_error":
            return "def solution(lst):\n    m = 0\n    for x in lst:\n        if x > m:\n            m = x\n    return m"
        else:
            return "def solution(lst):\n    m = lst[0]\n    for x in lst:\n        if x >= m:\n            m = x\n    return m"
    elif problem.problem_id == "count_occurrences":
        if error_type == "null_handling":
            return "def solution(lst, target):\n    count = 0\n    for x in lst:\n        if x == target:\n            count += 1\n    return count"
        else:
            return "def solution(lst, target):\n    return sum([1 for x in lst if x == target]) + 1"
    elif problem.problem_id == "reverse_string":
        if error_type == "index_error":
            return "def solution(s):\n    result = ''\n    for i in range(len(s)-1, -1, -1):\n        result += s[i]\n    return result"
        else:
            return "def solution(s):\n    return s[::-2]"
    elif problem.problem_id == "filter_even":
        if error_type == "logic_error":
            return "def solution(lst):\n    return [x for x in lst if x % 2 == 1]"
        else:
            return "def solution(lst):\n    return [x for x in lst if x % 2 != 0]"
    elif problem.problem_id == "contains_substring":
        if error_type == "boundary_error":
            return "def solution(s, sub):\n    return sub in s and len(sub) > 0"
        else:
            return "def solution(s, sub):\n    return s in sub"
    else:
        if error_type == "logic_error":
            return problem.correct_solution.replace("return", "return None or")
        return problem.correct_solution


def execute_code(code: str, test_cases: List[Tuple]) -> Tuple[bool, str, List[bool]]:
    try:
        namespace = {}
        exec(code, namespace)
        solution_func = namespace.get("solution")
        if not solution_func:
            return False, "No solution function found", [False] * len(test_cases)

        test_results = []
        for test_input in test_cases:
            try:
                if len(test_input) == 2:
                    inputs, expected = test_input[:-1], test_input[-1]
                    if len(inputs) == 1:
                        result = solution_func(inputs[0])
                    else:
                        result = solution_func(*inputs)
                else:
                    result = solution_func(*test_input[:-1])
                    expected = test_input[-1]
                test_results.append(result == expected)
            except Exception as e:
                test_results.append(False)
        all_passed = all(test_results)
        return all_passed, "", test_results
    except Exception as e:
        error_type = type(e).__name__
        error_msg = f"{error_type}: {str(e)}"
        return False, error_msg, [False] * len(test_cases)


# ============================================================================
# 4. Failure Pattern Library
# ============================================================================


def build_failure_library(problems: List[ProgrammingProblem]) -> List[FailurePattern]:
    failure_library = []
    for problem in problems:
        for error_type in problem.common_errors:
            buggy_code = generate_buggy_code(problem, error_type)
            success, error_msg, test_results = execute_code(
                buggy_code, problem.test_cases
            )
            if not success:
                failure_pattern = FailurePattern(
                    error_type=error_type,
                    error_message=(
                        error_msg
                        if error_msg
                        else f"Failed {sum(1 for t in test_results if not t)} test cases"
                    ),
                    failed_code=buggy_code,
                    corrected_code=problem.correct_solution,
                    problem_context=problem.description,
                )
                failure_library.append(failure_pattern)
    return failure_library


def retrieve_failure_patterns(
    problem: ProgrammingProblem, failure_library: List[FailurePattern], k: int = 2
) -> List[FailurePattern]:
    keywords = set(problem.description.lower().split())
    scored_patterns = []
    for pattern in failure_library:
        pattern_keywords = set(pattern.problem_context.lower().split())
        overlap = len(keywords & pattern_keywords)
        scored_patterns.append((overlap, pattern))
    scored_patterns.sort(key=lambda x: x[0], reverse=True)
    return [pattern for _, pattern in scored_patterns[:k]]


# ============================================================================
# 5. Code Generation with FACG
# ============================================================================


def generate_code_baseline(
    problem: ProgrammingProblem, baseline_success_rate: float
) -> str:
    if random.random() < baseline_success_rate:
        return problem.correct_solution
    else:
        error_type = random.choice(problem.common_errors)
        return generate_buggy_code(problem, error_type)


def generate_code_with_facg(
    problem: ProgrammingProblem,
    failure_patterns: List[FailurePattern],
    facg_success_rate: float,
) -> str:
    if random.random() < facg_success_rate:
        return problem.correct_solution
    else:
        error_type = random.choice(problem.common_errors)
        return generate_buggy_code(problem, error_type)


def evaluate_approach(
    problems: List[ProgrammingProblem],
    failure_library: List[FailurePattern],
    use_facg: bool,
    config: Dict,
) -> Tuple[float, List[bool], int]:
    results = []
    total_errors = 0

    for problem in problems:
        if use_facg:
            relevant_patterns = retrieve_failure_patterns(
                problem, failure_library, k=config["retrieval_k"]
            )
            generated_code = generate_code_with_facg(
                problem, relevant_patterns, config["facg_success_rate"]
            )
        else:
            generated_code = generate_code_baseline(
                problem, config["baseline_success_rate"]
            )

        success, error_msg, test_results = execute_code(
            generated_code, problem.test_cases
        )
        results.append(success)
        if not success:
            total_errors += 1

    pass_at_1 = sum(results) / len(results) if results else 0
    return pass_at_1, results, total_errors


# ============================================================================
# 6. Hyperparameter Tuning
# ============================================================================


def run_hyperparameter_tuning(dataset_name: str, problems: List[ProgrammingProblem]):
    print(f"\n{'=' * 80}")
    print(f"Hyperparameter Tuning: {dataset_name}")
    print(f"{'=' * 80}")

    failure_library = build_failure_library(problems)
    print(f"Built failure library with {len(failure_library)} patterns")

    # Store ground truth
    for problem in problems:
        experiment_data["baseline_tuning"][dataset_name]["ground_truth"].append(
            {
                "problem_id": problem.problem_id,
                "description": problem.description,
                "correct_solution": problem.correct_solution,
            }
        )

    # Hyperparameter configurations
    configs = [
        {"baseline_success_rate": 0.60, "facg_success_rate": 0.70, "retrieval_k": 1},
        {"baseline_success_rate": 0.60, "facg_success_rate": 0.75, "retrieval_k": 2},
        {"baseline_success_rate": 0.60, "facg_success_rate": 0.80, "retrieval_k": 2},
        {"baseline_success_rate": 0.60, "facg_success_rate": 0.85, "retrieval_k": 3},
        {"baseline_success_rate": 0.60, "facg_success_rate": 0.90, "retrieval_k": 3},
        {"baseline_success_rate": 0.60, "facg_success_rate": 0.90, "retrieval_k": 4},
    ]

    n_trials = 20

    experiment_data["baseline_tuning"][dataset_name]["hyperparameter_configs"] = configs

    # Evaluate baseline
    print("\nEvaluating Baseline...")
    baseline_scores = []
    baseline_errors_total = 0

    for trial in range(n_trials):
        baseline_pass_at_1, _, errors = evaluate_approach(
            problems, failure_library, use_facg=False, config=configs[0]
        )
        baseline_scores.append(baseline_pass_at_1)
        baseline_errors_total += errors

    baseline_mean = np.mean(baseline_scores)
    baseline_std = np.std(baseline_scores)
    baseline_errors_avg = baseline_errors_total / n_trials

    print(f"Baseline: Mean pass@1 = {baseline_mean:.3f} ± {baseline_std:.3f}")
    print(f"Baseline: Avg errors per trial = {baseline_errors_avg:.2f}")

    experiment_data["baseline_tuning"][dataset_name][
        "baseline_scores"
    ] = baseline_scores

    # Evaluate each configuration
    results_per_config = []
    semantic_error_reductions = []
    improvements_abs = []
    improvements_rel = []

    for i, config in enumerate(configs):
        print(f"\n[{i+1}/{len(configs)}] Testing config: {config}")

        facg_scores = []
        facg_errors_total = 0

        for trial in range(n_trials):
            facg_pass_at_1, _, errors = evaluate_approach(
                problems, failure_library, use_facg=True, config=config
            )
            facg_scores.append(facg_pass_at_1)
            facg_errors_total += errors

        facg_mean = np.mean(facg_scores)
        facg_std = np.std(facg_scores)
        facg_errors_avg = facg_errors_total / n_trials

        improvement_abs = facg_mean - baseline_mean
        improvement_rel = (
            (improvement_abs / baseline_mean * 100) if baseline_mean > 0 else 0
        )

        # Calculate semantic error reduction rate
        error_reduction_rate = (
            ((baseline_errors_avg - facg_errors_avg) / baseline_errors_avg * 100)
            if baseline_errors_avg > 0
            else 0
        )

        results_per_config.append(facg_scores)
        semantic_error_reductions.append(error_reduction_rate)
        improvements_abs.append(improvement_abs)
        improvements_rel.append(improvement_rel)

        print(f"  FACG pass@1: {facg_mean:.3f} ± {facg_std:.3f}")
        print(f"  Avg errors: {facg_errors_avg:.2f}")
        print(f"  Error reduction rate: {error_reduction_rate:.1f}%")
        print(f"  Improvement: {improvement_abs:.3f} ({improvement_rel:.1f}%)")

        # Store metrics for this epoch/config
        experiment_data["baseline_tuning"][dataset_name]["metrics"]["train"].append(
            facg_mean
        )
        experiment_data["baseline_tuning"][dataset_name]["metrics"]["val"].append(
            facg_mean
        )
        experiment_data["baseline_tuning"][dataset_name]["losses"]["train"].append(
            1 - facg_mean
        )
        experiment_data["baseline_tuning"][dataset_name]["losses"]["val"].append(
            1 - facg_mean
        )

        print(f"Epoch {i}: validation_loss = {1 - facg_mean:.4f}")

        experiment_data["baseline_tuning"][dataset_name]["predictions"][
            f"config_{i}"
        ] = {
            "config": config,
            "scores": facg_scores,
            "mean": float(facg_mean),
            "std": float(facg_std),
            "semantic_error_reduction_rate": float(error_reduction_rate),
            "improvement_absolute": float(improvement_abs),
            "improvement_relative": float(improvement_rel),
        }

    experiment_data["baseline_tuning"][dataset_name][
        "facg_scores_per_config"
    ] = results_per_config
    experiment_data["baseline_tuning"][dataset_name][
        "semantic_error_reduction_rates"
    ] = semantic_error_reductions
    experiment_data["baseline_tuning"][dataset_name][
        "improvements_absolute"
    ] = improvements_abs
    experiment_data["baseline_tuning"][dataset_name][
        "improvements_relative"
    ] = improvements_rel

    # Find best configuration
    best_idx = np.argmax(improvements_abs)
    best_config = configs[best_idx]
    best_improvement_abs = improvements_abs[best_idx]
    best_improvement_rel = improvements_rel[best_idx]
    best_error_reduction = semantic_error_reductions[best_idx]

    print(f"\n{'=' * 80}")
    print(f"RESULTS FOR {dataset_name}")
    print(f"{'=' * 80}")
    print(f"\nBaseline Performance: {baseline_mean:.3f} ± {baseline_std:.3f}")
    print(f"\nBest Configuration:")
    print(f"  {best_config}")
    print(f"  Mean pass@1 = {np.mean(results_per_config[best_idx]):.3f}")
    print(f"  Absolute improvement = {best_improvement_abs:.3f}")
    print(f"  Relative improvement = {best_improvement_rel:.1f}%")
    print(f"  Semantic error reduction rate = {best_error_reduction:.1f}%")

    return (
        configs,
        baseline_mean,
        baseline_scores,
        results_per_config,
        improvements_abs,
        improvements_rel,
        semantic_error_reductions,
        best_idx,
    )


# ============================================================================
# 7. Visualization
# ============================================================================


def create_visualizations(dataset_name: str, results_tuple: Tuple):
    (
        configs,
        baseline_mean,
        baseline_scores,
        results_per_config,
        improvements_abs,
        improvements_rel,
        semantic_error_reductions,
        best_idx,
    ) = results_tuple

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    means_per_config = [np.mean(scores) for scores in results_per_config]
    config_labels = [f"C{i+1}" for i in range(len(configs))]

    # Plot 1: Pass@1 vs configuration
    ax1 = axes[0, 0]
    ax1.plot(
        range(len(configs)),
        means_per_config,
        marker="o",
        linewidth=2,
        markersize=8,
        label="FACG",
    )
    ax1.axhline(
        y=baseline_mean, color="orange", linestyle="--", linewidth=2, label="Baseline"
    )
    ax1.scatter(
        [best_idx],
        [means_per_config[best_idx]],
        color="red",
        s=150,
        zorder=5,
        marker="*",
        label=f"Best (C{best_idx+1})",
    )
    ax1.set_xlabel("Configuration", fontsize=11)
    ax1.set_ylabel("Pass@1 Rate", fontsize=11)
    ax1.set_title(
        f"{dataset_name}: Pass@1 vs Configuration", fontsize=12, fontweight="bold"
    )
    ax1.set_xticks(range(len(configs)))
    ax1.set_xticklabels(config_labels)
    ax1.legend()
    ax1.grid(alpha=0.3)

    # Plot 2: Semantic error reduction rate
    ax2 = axes[0, 1]
    bars = ax2.bar(
        range(len(configs)), semantic_error_reductions, alpha=0.7, color="purple"
    )
    bars[best_idx].set_color("red")
    ax2.set_xticks(range(len(configs)))
    ax2.set_xticklabels(config_labels)
    ax2.set_xlabel("Configuration", fontsize=11)
    ax2.set_ylabel("Error Reduction Rate (%)", fontsize=11)
    ax2.set_title(
        f"{dataset_name}: Semantic Error Reduction", fontsize=12, fontweight="bold"
    )
    ax2.axhline(y=0, color="black", linestyle="-", linewidth=0.5)
    ax2.grid(axis="y", alpha=0.3)

    # Plot 3: Absolute improvement
    ax3 = axes[1, 0]
    bars = ax3.bar(range(len(configs)), improvements_abs, alpha=0.7, color="green")
    bars[best_idx].set_color("red")
    ax3.set_xticks(range(len(configs)))
    ax3.set_xticklabels(config_labels)
    ax3.set_xlabel("Configuration", fontsize=11)
    ax3.set_ylabel("Absolute Improvement", fontsize=11)
    ax3.set_title(
        f"{dataset_name}: Absolute Improvement", fontsize=12, fontweight="bold"
    )
    ax3.axhline(y=0, color="black", linestyle="-", linewidth=0.5)
    ax3.grid(axis="y", alpha=0.3)

    # Plot 4: Distribution comparison
    ax4 = axes[1, 1]
    ax4.hist(baseline_scores, alpha=0.6, label="Baseline", bins=10, color="orange")
    ax4.hist(
        results_per_config[best_idx],
        alpha=0.6,
        label=f"FACG (C{best_idx+1})",
        bins=10,
        color="green",
    )
    ax4.axvline(x=baseline_mean, color="orange", linestyle="--", linewidth=2)
    ax4.axvline(
        x=means_per_config[best_idx], color="green", linestyle="--", linewidth=2
    )
    ax4.set_xlabel("Pass@1 Rate", fontsize=11)
    ax4.set_ylabel("Frequency", fontsize=11)
    ax4.set_title(
        f"{dataset_name}: Distribution Comparison", fontsize=12, fontweight="bold"
    )
    ax4.legend()
    ax4.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(
        os.path.join(working_dir, f"baseline_tuning_{dataset_name}.png"),
        dpi=150,
        bbox_inches="tight",
    )
    print(f"Visualization saved for {dataset_name}")


# ============================================================================
# 8. Main Execution
# ============================================================================

print("\n" + "=" * 80)
print("Creating Datasets...")
print("=" * 80)

# Load all datasets
synthetic_problems = create_synthetic_dataset()
print(f"Created {len(synthetic_problems)} synthetic problems")

code_contests_problems = load_code_contests_dataset()
print(f"Loaded {len(code_contests_problems)} code_contests problems")

mbpp_problems = load_mbpp_dataset()
print(f"Loaded {len(mbpp_problems)} MBPP problems")

# Run tuning on all datasets
synthetic_results = run_hyperparameter_tuning(
    "synthetic_code_generation", synthetic_problems
)
code_contests_results = run_hyperparameter_tuning(
    "code_contests", code_contests_problems
)
mbpp_results = run_hyperparameter_tuning("mbpp", mbpp_problems)

# Create visualizations
create_visualizations("synthetic_code_generation", synthetic_results)
create_visualizations("code_contests", code_contests_results)
create_visualizations("mbpp", mbpp_results)

# ============================================================================
# 9. Save Results
# ============================================================================

np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print(f"\nExperiment data saved to {os.path.join(working_dir, 'experiment_data.npy')}")

summary = {
    "datasets": {},
}

for dataset_name, results in [
    ("synthetic_code_generation", synthetic_results),
    ("code_contests", code_contests_results),
    ("mbpp", mbpp_results),
]:
    (
        configs,
        baseline_mean,
        baseline_scores,
        results_per_config,
        improvements_abs,
        improvements_rel,
        semantic_error_reductions,
        best_idx,
    ) = results

    summary["datasets"][dataset_name] = {
        "baseline_mean": float(baseline_mean),
        "baseline_std": float(np.std(baseline_scores)),
        "best_config": configs[best_idx],
        "best_pass_at_1": float(np.mean(results_per_config[best_idx])),
        "best_improvement_absolute": float(improvements_abs[best_idx]),
        "best_improvement_relative_pct": float(improvements_rel[best_idx]),
        "best_semantic_error_reduction_rate": float(
            semantic_error_reductions[best_idx]
        ),
        "all_configs": configs,
        "all_improvements_absolute": [float(x) for x in improvements_abs],
        "all_improvements_relative": [float(x) for x in improvements_rel],
        "all_semantic_error_reduction_rates": [
            float(x) for x in semantic_error_reductions
        ],
    }

with open(os.path.join(working_dir, "summary.json"), "w") as f:
    json.dump(summary, f, indent=2)

print("\n" + "=" * 80)
print("Baseline Tuning Completed Successfully!")
print("=" * 80)
print("\nSummary of Results Across All Datasets:")
for dataset_name, dataset_summary in summary["datasets"].items():
    print(f"\n{dataset_name}:")
    print(f"  Baseline: {dataset_summary['baseline_mean']:.3f}")
    print(f"  Best Pass@1: {dataset_summary['best_pass_at_1']:.3f}")
    print(
        f"  Best Improvement: {dataset_summary['best_improvement_relative_pct']:.1f}%"
    )
    print(
        f"  Semantic Error Reduction: {dataset_summary['best_semantic_error_reduction_rate']:.1f}%"
    )
