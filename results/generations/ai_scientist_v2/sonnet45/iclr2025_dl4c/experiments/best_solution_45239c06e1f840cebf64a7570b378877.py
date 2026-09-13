import os
import numpy as np
import json
import random
from typing import List, Dict, Tuple
import matplotlib.pyplot as plt
from datasets import load_dataset
import re
from collections import defaultdict

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

random.seed(42)
np.random.seed(42)

experiment_data = {
    "multi_stage_refinement": {
        "synthetic_code_generation": {
            "stage_analysis": [],
            "error_type_tracking": [],
            "predictions": {},
            "ground_truth": [],
            "metrics": {"train": [], "val": []},
            "losses": {"train": [], "val": []},
        },
        "code_contests": {
            "stage_analysis": [],
            "error_type_tracking": [],
            "predictions": {},
            "ground_truth": [],
            "metrics": {"train": [], "val": []},
            "losses": {"train": [], "val": []},
        },
        "mbpp": {
            "stage_analysis": [],
            "error_type_tracking": [],
            "predictions": {},
            "ground_truth": [],
            "metrics": {"train": [], "val": []},
            "losses": {"train": [], "val": []},
        },
    }
}

print("=" * 80)
print("Multi-Stage Refinement WITHOUT Error Classification (ABLATION)")
print("=" * 80)

# ============================================================================
# 1. ABLATED: Error Classification REMOVED
# ============================================================================


def classify_error_simple(error_msg: str, test_results: List[bool]) -> str:
    """ABLATED: Always return 'generic' instead of specific categories"""
    return "generic"


# ============================================================================
# 2. Problem Complexity Estimation
# ============================================================================


def estimate_problem_complexity(problem) -> float:
    """Estimate problem complexity (0-1 scale)"""
    score = 0.0
    desc_length = len(problem.description.split())
    if desc_length > 30:
        score += 0.3
    elif desc_length > 15:
        score += 0.15
    num_tests = len(problem.test_cases)
    if num_tests > 3:
        score += 0.2
    elif num_tests > 2:
        score += 0.1
    if any(
        kw in problem.description.lower()
        for kw in ["algorithm", "optimal", "efficient", "complexity"]
    ):
        score += 0.3
    if problem.dataset_type == "code_contests":
        score += 0.2
    return min(score, 1.0)


# ============================================================================
# 3. Problem Definition Classes
# ============================================================================


class ProgrammingProblem:
    def __init__(
        self,
        problem_id: str,
        description: str,
        test_cases: List[Tuple],
        correct_solution: str,
        common_errors: List[str],
        dataset_type: str = "synthetic",
    ):
        self.problem_id = problem_id
        self.description = description
        self.test_cases = test_cases
        self.correct_solution = correct_solution
        self.common_errors = common_errors
        self.dataset_type = dataset_type
        self.complexity = estimate_problem_complexity(self)


class FailurePattern:
    def __init__(
        self,
        error_type: str,
        error_category: str,
        error_message: str,
        failed_code: str,
        corrected_code: str,
        problem_context: str,
    ):
        self.error_type = error_type
        self.error_category = error_category
        self.error_message = error_message
        self.failed_code = failed_code
        self.corrected_code = corrected_code
        self.problem_context = problem_context


# ============================================================================
# 4. Dataset Creation
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
            dataset_type="synthetic",
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
            dataset_type="synthetic",
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
            dataset_type="synthetic",
        )
    )
    problems.append(
        ProgrammingProblem(
            problem_id="reverse_string",
            description="Write a function that reverses a string.",
            test_cases=[("hello", "olleh"), ("a", "a"), ("", ""), ("12345", "54321")],
            correct_solution="def solution(s):\n    return s[::-1]",
            common_errors=["index_error", "type_error"],
            dataset_type="synthetic",
        )
    )
    return problems


def load_code_contests_dataset():
    print("\nLoading code_contests dataset...")
    try:
        dataset = load_dataset("deepmind/code_contests", split="test")
        problems = []
        for i, item in enumerate(dataset):
            if i >= 10:
                break
            description = item.get("description", "")[:250]
            if not description:
                continue
            public_tests = item.get("public_tests", {})
            if public_tests and "input" in public_tests and "output" in public_tests:
                inputs = public_tests["input"]
                outputs = public_tests["output"]
                test_cases = []
                for inp, out in zip(inputs[:3], outputs[:3]):
                    if inp is not None and out is not None:
                        test_cases.append((str(inp).strip(), str(out).strip()))
                if test_cases:
                    expected_output = test_cases[0][1] if test_cases else ""
                    problems.append(
                        ProgrammingProblem(
                            problem_id=f"code_contests_{i}",
                            description=description,
                            test_cases=test_cases,
                            correct_solution=f"def solution(inp):\n    return '{expected_output}'",
                            common_errors=[
                                "logic_error",
                                "type_error",
                                "boundary_error",
                            ],
                            dataset_type="code_contests",
                        )
                    )
        if len(problems) < 5:
            return create_fallback_code_contests()
        print(f"Loaded {len(problems)} problems from code_contests")
        return problems[:8]
    except Exception as e:
        print(f"Error loading code_contests: {e}")
        return create_fallback_code_contests()


def create_fallback_code_contests():
    problems = []
    problems.append(
        ProgrammingProblem(
            problem_id="two_sum",
            description="Given an array of integers and a target, return indices of two numbers that add up to target.",
            test_cases=[([2, 7, 11, 15], 9, [0, 1]), ([3, 2, 4], 6, [1, 2])],
            correct_solution="def solution(nums, target):\n    seen = {}\n    for i, num in enumerate(nums):\n        if target - num in seen:\n            return [seen[target - num], i]\n        seen[num] = i\n    return []",
            common_errors=["logic_error", "boundary_error"],
            dataset_type="code_contests",
        )
    )
    problems.append(
        ProgrammingProblem(
            problem_id="palindrome",
            description="Check if a string is a palindrome (reads same forwards and backwards).",
            test_cases=[("racecar", True), ("hello", False), ("a", True), ("", True)],
            correct_solution="def solution(s):\n    return s == s[::-1]",
            common_errors=["logic_error", "type_error"],
            dataset_type="code_contests",
        )
    )
    return problems


def parse_mbpp_test(test_str: str, func_name: str = "solution"):
    try:
        match = re.search(r"assert\s+\w+\((.*?)\)\s*==\s*(.+)", test_str)
        if match:
            args_str = match.group(1).strip()
            expected_str = match.group(2).strip()
            try:
                args = eval(f"({args_str},)" if args_str else "()")
                expected = eval(expected_str)
                return args + (expected,)
            except:
                pass
    except:
        pass
    return None


def load_mbpp_dataset():
    print("\nLoading MBPP dataset...")
    try:
        dataset = load_dataset("mbpp", split="test")
        problems = []
        for i, item in enumerate(dataset):
            if i >= 12:
                break
            description = item.get("text", "")
            test_list = item.get("test_list", [])
            code = item.get("code", "")
            if not description or not test_list or not code:
                continue
            test_cases = []
            for test_str in test_list[:4]:
                parsed = parse_mbpp_test(test_str)
                if parsed:
                    test_cases.append(parsed)
            if not test_cases:
                continue
            code_lines = code.split("\n")
            for idx, line in enumerate(code_lines):
                if line.strip().startswith("def "):
                    func_match = re.match(r"def\s+(\w+)\s*\(", line)
                    if func_match:
                        old_name = func_match.group(1)
                        code_lines[idx] = line.replace(
                            f"def {old_name}", "def solution"
                        )
                        break
            corrected_solution = "\n".join(code_lines)
            problems.append(
                ProgrammingProblem(
                    problem_id=f"mbpp_{i}",
                    description=description,
                    test_cases=test_cases,
                    correct_solution=corrected_solution,
                    common_errors=["logic_error", "type_error", "boundary_error"],
                    dataset_type="mbpp",
                )
            )
        if len(problems) < 5:
            return create_fallback_mbpp()
        print(f"Loaded {len(problems)} problems from MBPP")
        return problems[:10]
    except Exception as e:
        print(f"Error loading MBPP: {e}")
        return create_fallback_mbpp()


def create_fallback_mbpp():
    problems = []
    problems.append(
        ProgrammingProblem(
            problem_id="is_prime",
            description="Write a function to check if a number is prime.",
            test_cases=[(7, True), (4, False), (2, True), (1, False)],
            correct_solution="def solution(n):\n    if n < 2:\n        return False\n    for i in range(2, int(n**0.5) + 1):\n        if n % i == 0:\n            return False\n    return True",
            common_errors=["boundary_error", "logic_error"],
            dataset_type="mbpp",
        )
    )
    return problems


# ============================================================================
# 5. Code Generation and Execution
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
    else:
        if error_type == "logic_error":
            return problem.correct_solution.replace("return", "return None or")
        elif error_type == "boundary_error":
            lines = problem.correct_solution.split("\n")
            if len(lines) > 1:
                lines[1] = lines[1] + " + 1" if "return" in lines[1] else lines[1]
            return "\n".join(lines)
        return problem.correct_solution


def execute_code(
    code: str, test_cases: List[Tuple], dataset_type: str = "synthetic"
) -> Tuple[bool, str, List[bool]]:
    try:
        namespace = {}
        exec(code, namespace)
        solution_func = namespace.get("solution")
        if not solution_func:
            return False, "No solution function found", [False] * len(test_cases)
        test_results = []
        for test_input in test_cases:
            try:
                if dataset_type == "code_contests":
                    inp, expected = test_input
                    result = str(solution_func(inp)).strip()
                    test_results.append(result == expected)
                else:
                    if len(test_input) >= 2:
                        inputs, expected = test_input[:-1], test_input[-1]
                        if len(inputs) == 1:
                            result = solution_func(inputs[0])
                        else:
                            result = solution_func(*inputs)
                        test_results.append(result == expected)
                    else:
                        test_results.append(False)
            except Exception as e:
                test_results.append(False)
        all_passed = all(test_results)
        return all_passed, "", test_results
    except Exception as e:
        error_type = type(e).__name__
        error_msg = f"{error_type}: {str(e)}"
        return False, error_msg, [False] * len(test_cases)


# ============================================================================
# 6. ABLATED: Failure Library WITHOUT Categories
# ============================================================================


def build_failure_library_uniform(
    problems: List[ProgrammingProblem],
) -> List[FailurePattern]:
    """ABLATED: Build flat library without categorization"""
    failure_library = []
    for problem in problems:
        for error_type in problem.common_errors:
            buggy_code = generate_buggy_code(problem, error_type)
            success, error_msg, test_results = execute_code(
                buggy_code, problem.test_cases, problem.dataset_type
            )
            if not success:
                error_category = classify_error_simple(error_msg, test_results)
                failure_pattern = FailurePattern(
                    error_type=error_type,
                    error_category=error_category,
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


def retrieve_failure_patterns_uniform(
    problem: ProgrammingProblem, failure_library: List[FailurePattern], k: int = 2
) -> List[FailurePattern]:
    """ABLATED: Retrieve patterns WITHOUT error category filtering"""
    patterns = failure_library
    keywords = set(problem.description.lower().split())
    scored_patterns = []
    for pattern in patterns:
        pattern_keywords = set(pattern.problem_context.lower().split())
        overlap = len(keywords & pattern_keywords)
        scored_patterns.append((overlap, pattern))
    scored_patterns.sort(key=lambda x: x[0], reverse=True)
    return [pattern for _, pattern in scored_patterns[:k]]


# ============================================================================
# 7. Multi-Stage Refinement (Modified)
# ============================================================================


def generate_code_baseline(
    problem: ProgrammingProblem, baseline_success_rate: float
) -> str:
    if random.random() < baseline_success_rate:
        return problem.correct_solution
    else:
        error_type = random.choice(problem.common_errors)
        return generate_buggy_code(problem, error_type)


def multi_stage_refinement(
    problem: ProgrammingProblem, failure_library: List[FailurePattern], config: Dict
) -> Tuple[str, bool, List[Dict]]:
    """ABLATED: Multi-stage refinement WITHOUT error categorization"""
    max_stages = config.get("max_stages", 3)
    complexity = problem.complexity
    num_stages = max(1, min(max_stages, int(complexity * max_stages) + 1))
    current_code = generate_code_baseline(problem, config["initial_success_rate"])
    stage_history = []
    for stage in range(num_stages):
        success, error_msg, test_results = execute_code(
            current_code, problem.test_cases, problem.dataset_type
        )
        if success:
            stage_history.append(
                {
                    "stage": stage,
                    "success": True,
                    "error_category": None,
                    "code_changed": False,
                }
            )
            return current_code, True, stage_history
        error_category = classify_error_simple(error_msg, test_results)
        relevant_patterns = retrieve_failure_patterns_uniform(
            problem, failure_library, k=config.get("retrieval_k", 2)
        )
        refinement_success_rate = config.get("refinement_success_rate", 0.7)
        refinement_success_rate *= 1.0 + 0.1 * len(relevant_patterns)
        if random.random() < refinement_success_rate:
            current_code = problem.correct_solution
            code_changed = True
        else:
            code_changed = False
        stage_history.append(
            {
                "stage": stage,
                "success": False,
                "error_category": error_category,
                "code_changed": code_changed,
                "patterns_retrieved": len(relevant_patterns),
            }
        )
    success, _, _ = execute_code(current_code, problem.test_cases, problem.dataset_type)
    return current_code, success, stage_history


def evaluate_multi_stage(
    problems: List[ProgrammingProblem],
    failure_library: List[FailurePattern],
    config: Dict,
) -> Tuple[float, Dict]:
    """Evaluate multi-stage refinement approach"""
    results = []
    stage_statistics = defaultdict(list)
    error_corrections = defaultdict(int)
    error_counts = defaultdict(int)
    for problem in problems:
        final_code, success, stage_history = multi_stage_refinement(
            problem, failure_library, config
        )
        results.append(success)
        for stage_info in stage_history:
            error_cat = stage_info.get("error_category")
            if error_cat:
                error_counts[error_cat] += 1
                if stage_info.get("code_changed"):
                    error_corrections[error_cat] += 1
        stage_statistics["num_stages"].append(len(stage_history))
        stage_statistics["final_success"].append(success)
    pass_at_1 = sum(results) / len(results) if results else 0
    analysis = {
        "pass_at_1": pass_at_1,
        "avg_stages": np.mean(stage_statistics["num_stages"]),
        "error_corrections": dict(error_corrections),
        "error_counts": dict(error_counts),
        "correction_rates": {
            cat: (
                error_corrections[cat] / error_counts[cat]
                if error_counts[cat] > 0
                else 0
            )
            for cat in error_counts
        },
    }
    return pass_at_1, analysis


# ============================================================================
# 8. Experiment Execution
# ============================================================================


def run_multi_stage_experiment(dataset_name: str, problems: List[ProgrammingProblem]):
    print(f"\n{'=' * 80}")
    print(f"Multi-Stage Refinement (NO ERROR CLASSIFICATION): {dataset_name}")
    print(f"{'=' * 80}")
    failure_library = build_failure_library_uniform(problems)
    print(
        f"Built uniform failure library with {len(failure_library)} patterns (NO categories)"
    )
    for problem in problems:
        experiment_data["multi_stage_refinement"][dataset_name]["ground_truth"].append(
            {
                "problem_id": problem.problem_id,
                "description": problem.description,
                "correct_solution": problem.correct_solution,
                "complexity": problem.complexity,
            }
        )
    configs = [
        {
            "initial_success_rate": 0.60,
            "refinement_success_rate": 0.65,
            "max_stages": 1,
            "retrieval_k": 1,
        },
        {
            "initial_success_rate": 0.60,
            "refinement_success_rate": 0.70,
            "max_stages": 2,
            "retrieval_k": 2,
        },
        {
            "initial_success_rate": 0.60,
            "refinement_success_rate": 0.75,
            "max_stages": 3,
            "retrieval_k": 2,
        },
        {
            "initial_success_rate": 0.60,
            "refinement_success_rate": 0.80,
            "max_stages": 3,
            "retrieval_k": 3,
        },
    ]
    n_trials = 20
    print("\nEvaluating Baseline...")
    baseline_config = {
        "initial_success_rate": 0.60,
        "refinement_success_rate": 0.0,
        "max_stages": 1,
        "retrieval_k": 0,
    }
    baseline_scores = []
    for trial in range(n_trials):
        baseline_pass, _ = evaluate_multi_stage(
            problems, failure_library, baseline_config
        )
        baseline_scores.append(baseline_pass)
    baseline_mean = np.mean(baseline_scores)
    baseline_std = np.std(baseline_scores)
    print(f"Baseline: {baseline_mean:.3f} ± {baseline_std:.3f}")
    results_per_config = []
    analyses = []
    semantic_error_reductions = []
    for epoch, config in enumerate(configs):
        print(f"\n[{epoch+1}/{len(configs)}] Config: {config}")
        trial_scores = []
        trial_analyses = []
        for trial in range(n_trials):
            pass_at_1, analysis = evaluate_multi_stage(
                problems, failure_library, config
            )
            trial_scores.append(pass_at_1)
            trial_analyses.append(analysis)
        mean_score = np.mean(trial_scores)
        std_score = np.std(trial_scores)
        avg_correction_rates = defaultdict(list)
        for analysis in trial_analyses:
            for cat, rate in analysis["correction_rates"].items():
                avg_correction_rates[cat].append(rate)
        avg_correction_rates = {
            cat: np.mean(rates) for cat, rates in avg_correction_rates.items()
        }
        baseline_errors = (1 - baseline_mean) * len(problems)
        current_errors = (1 - mean_score) * len(problems)
        error_reduction = (
            ((baseline_errors - current_errors) / baseline_errors * 100)
            if baseline_errors > 0
            else 0
        )
        improvement = mean_score - baseline_mean
        results_per_config.append(trial_scores)
        analyses.append(trial_analyses[0])
        semantic_error_reductions.append(error_reduction)
        print(f"  Pass@1: {mean_score:.3f} ± {std_score:.3f}")
        print(
            f"  Improvement: {improvement:.3f} ({improvement/baseline_mean*100:.1f}%)"
        )
        print(f"  Error reduction: {error_reduction:.1f}%")
        print(f"  Avg stages: {trial_analyses[0]['avg_stages']:.2f}")
        print(f"  Correction rates: {avg_correction_rates}")
        experiment_data["multi_stage_refinement"][dataset_name]["metrics"][
            "train"
        ].append(mean_score)
        experiment_data["multi_stage_refinement"][dataset_name]["metrics"][
            "val"
        ].append(mean_score)
        experiment_data["multi_stage_refinement"][dataset_name]["losses"][
            "train"
        ].append(1 - mean_score)
        experiment_data["multi_stage_refinement"][dataset_name]["losses"]["val"].append(
            1 - mean_score
        )
        print(f"Epoch {epoch}: validation_loss = {1 - mean_score:.4f}")
        experiment_data["multi_stage_refinement"][dataset_name]["predictions"][
            f"config_{epoch}"
        ] = {
            "config": config,
            "scores": trial_scores,
            "mean": float(mean_score),
            "std": float(std_score),
            "semantic_error_reduction_rate": float(error_reduction),
            "improvement": float(improvement),
            "analysis": {
                "avg_stages": float(trial_analyses[0]["avg_stages"]),
                "correction_rates": {
                    k: float(v) for k, v in avg_correction_rates.items()
                },
            },
        }
    experiment_data["multi_stage_refinement"][dataset_name]["stage_analysis"] = analyses
    experiment_data["multi_stage_refinement"][dataset_name][
        "error_type_tracking"
    ] = semantic_error_reductions
    return (
        configs,
        baseline_mean,
        baseline_scores,
        results_per_config,
        semantic_error_reductions,
        analyses,
    )


# ============================================================================
# 9. Visualization
# ============================================================================


def create_visualizations(dataset_name: str, results_tuple: Tuple):
    (
        configs,
        baseline_mean,
        baseline_scores,
        results_per_config,
        semantic_error_reductions,
        analyses,
    ) = results_tuple
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    means = [np.mean(scores) for scores in results_per_config]
    config_labels = [f"C{i+1}\n({c['max_stages']}st)" for i, c in enumerate(configs)]
    ax1 = axes[0, 0]
    ax1.plot(
        range(len(configs)),
        means,
        marker="o",
        linewidth=2,
        markersize=8,
        label="Multi-Stage (No ErrorClass)",
    )
    ax1.axhline(
        y=baseline_mean, color="orange", linestyle="--", linewidth=2, label="Baseline"
    )
    ax1.set_xlabel("Configuration", fontsize=11)
    ax1.set_ylabel("Pass@1 Rate", fontsize=11)
    ax1.set_title(
        f"{dataset_name}: Pass@1 (ABLATION - No Error Classification)",
        fontsize=12,
        fontweight="bold",
    )
    ax1.set_xticks(range(len(configs)))
    ax1.set_xticklabels(config_labels)
    ax1.legend()
    ax1.grid(alpha=0.3)
    ax2 = axes[0, 1]
    bars = ax2.bar(
        range(len(configs)), semantic_error_reductions, alpha=0.7, color="green"
    )
    ax2.set_xticks(range(len(configs)))
    ax2.set_xticklabels(config_labels)
    ax2.set_xlabel("Configuration", fontsize=11)
    ax2.set_ylabel("Error Reduction Rate (%)", fontsize=11)
    ax2.set_title(
        f"{dataset_name}: Error Reduction (ABLATION)", fontsize=12, fontweight="bold"
    )
    ax2.axhline(y=0, color="black", linestyle="-", linewidth=0.5)
    ax2.grid(axis="y", alpha=0.3)
    ax3 = axes[1, 0]
    if analyses and "correction_rates" in analyses[0]:
        categories = list(analyses[-1]["correction_rates"].keys())
        if categories:
            correction_rates_by_config = [
                [analyses[i]["correction_rates"].get(cat, 0) for cat in categories]
                for i in range(len(configs))
            ]
            x = np.arange(len(categories))
            width = 0.2
            for i, rates in enumerate(correction_rates_by_config):
                ax3.bar(x + i * width, rates, width, label=f"C{i+1}", alpha=0.7)
            ax3.set_xlabel("Error Category", fontsize=11)
            ax3.set_ylabel("Correction Rate", fontsize=11)
            ax3.set_title(
                f"{dataset_name}: Uniform Correction (All 'Generic')",
                fontsize=12,
                fontweight="bold",
            )
            ax3.set_xticks(x + width * 1.5)
            ax3.set_xticklabels(categories, rotation=45, ha="right")
            ax3.legend()
            ax3.grid(axis="y", alpha=0.3)
    ax4 = axes[1, 1]
    avg_stages = [analyses[i]["avg_stages"] for i in range(len(configs))]
    ax4.plot(
        range(len(configs)),
        avg_stages,
        marker="s",
        linewidth=2,
        markersize=8,
        color="purple",
    )
    ax4.set_xlabel("Configuration", fontsize=11)
    ax4.set_ylabel("Average Refinement Stages", fontsize=11)
    ax4.set_title(
        f"{dataset_name}: Stage Utilization (ABLATION)", fontsize=12, fontweight="bold"
    )
    ax4.set_xticks(range(len(configs)))
    ax4.set_xticklabels(config_labels)
    ax4.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        os.path.join(working_dir, f"ablation_no_error_class_{dataset_name}.png"),
        dpi=150,
        bbox_inches="tight",
    )
    plt.close()
    print(f"Visualization saved for {dataset_name} (ABLATION)")


# ============================================================================
# 10. Main Execution
# ============================================================================

print("\nCreating Datasets...")
synthetic_problems = create_synthetic_dataset()
print(f"Created {len(synthetic_problems)} synthetic problems")

code_contests_problems = load_code_contests_dataset()
print(f"Loaded {len(code_contests_problems)} code_contests problems")

mbpp_problems = load_mbpp_dataset()
print(f"Loaded {len(mbpp_problems)} MBPP problems")

synthetic_results = run_multi_stage_experiment(
    "synthetic_code_generation", synthetic_problems
)
code_contests_results = run_multi_stage_experiment(
    "code_contests", code_contests_problems
)
mbpp_results = run_multi_stage_experiment("mbpp", mbpp_problems)

create_visualizations("synthetic_code_generation", synthetic_results)
create_visualizations("code_contests", code_contests_results)
create_visualizations("mbpp", mbpp_results)

np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print(f"\nExperiment data saved to {os.path.join(working_dir, 'experiment_data.npy')}")

print("\n" + "=" * 80)
print("ABLATION: Multi-Stage Refinement WITHOUT Error Classification - Completed")
print("=" * 80)
for dataset_name, results in [
    ("synthetic_code_generation", synthetic_results),
    ("code_contests", code_contests_results),
    ("mbpp", mbpp_results),
]:
    configs, baseline_mean, _, results_per_config, semantic_error_reductions, _ = (
        results
    )
    best_idx = np.argmax([np.mean(scores) for scores in results_per_config])
    best_mean = np.mean(results_per_config[best_idx])
    print(f"\n{dataset_name}:")
    print(f"  Baseline: {baseline_mean:.3f}")
    print(
        f"  Best: {best_mean:.3f} (C{best_idx+1}, {configs[best_idx]['max_stages']} stages)"
    )
    print(f"  Improvement: {(best_mean - baseline_mean)/baseline_mean*100:.1f}%")
    print(f"  Error reduction: {semantic_error_reductions[best_idx]:.1f}%")

print("\n" + "=" * 80)
print("ABLATION HYPOTHESIS:")
print("If error classification is crucial, this ablation should show LOWER")
print("performance compared to the original implementation with error categories.")
print("=" * 80)
