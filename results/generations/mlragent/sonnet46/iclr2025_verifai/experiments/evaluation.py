"""
Evaluation utilities for ExecGuide experiments.
Computes pass@k, SCR, FPC, IOR, and other metrics.
"""

import re
import ast
import time
import signal
import contextlib
import numpy as np
from typing import List, Dict, Tuple, Optional
from datasets import load_dataset


def load_humaneval(num_problems: Optional[int] = None) -> list:
    """Load HumanEval dataset."""
    dataset = load_dataset("openai_humaneval", split="test")
    problems = list(dataset)
    if num_problems:
        problems = problems[:num_problems]
    return problems


def extract_function_body(generated_code: str, prompt: str, entry_point: str) -> str:
    """
    Extract the complete function from generated code.
    Returns the full executable code including the function definition.
    """
    # Try to get just the function definition
    full_code = prompt + generated_code if not generated_code.startswith("def ") else generated_code

    # Find the function
    pattern = rf"def {re.escape(entry_point)}\s*\("
    match = re.search(pattern, full_code)
    if not match:
        return full_code

    start_idx = match.start()
    code_from_func = full_code[start_idx:]

    # Find end of function by parsing
    try:
        # Try to parse and find the function end
        lines = code_from_func.split('\n')
        func_lines = []
        in_func = True
        func_indent = None

        for i, line in enumerate(lines):
            if i == 0:
                func_lines.append(line)
                continue

            stripped = line.lstrip()
            if not stripped or stripped.startswith('#'):
                func_lines.append(line)
                continue

            # Determine indentation
            indent = len(line) - len(stripped)

            if i == 1 and stripped:
                # First non-empty line after def: set function body indent
                func_indent = indent

            if func_indent is not None and indent < func_indent and stripped and i > 1:
                # We're back at or below function level - stop
                if not (stripped.startswith('@') or stripped.startswith('def ') or stripped.startswith('class ')):
                    break

            func_lines.append(line)

        return '\n'.join(func_lines)
    except Exception:
        return code_from_func


def run_humaneval_test(code: str, test: str, entry_point: str, timeout: float = 5.0) -> bool:
    """
    Run HumanEval test cases against generated code.
    Returns True if all tests pass.
    """
    try:
        # Prepare the test code
        test_code = code + "\n\n" + test + "\n\ncheck(" + entry_point + ")"

        # Execute with timeout
        def timeout_handler(signum, frame):
            raise TimeoutError("Execution timeout")

        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(int(timeout) + 1)

        try:
            namespace = {}
            exec(test_code, namespace)
            signal.alarm(0)
            return True
        except TimeoutError:
            return False
        except AssertionError:
            return False
        except Exception:
            return False
        finally:
            signal.signal(signal.SIGALRM, old_handler)
            signal.alarm(0)

    except Exception:
        return False


def compute_pass_at_k(n: int, c: int, k: int) -> float:
    """
    Compute pass@k metric.
    n: total number of samples
    c: number of correct samples
    k: k value
    """
    if n - c < k:
        return 1.0
    return 1.0 - np.prod(
        1.0 - k / np.arange(n - c + 1, n + 1)
    )


def evaluate_method(
    method_name: str,
    problems: list,
    generate_fn,
    num_samples: int = 1,
    verbose: bool = True,
) -> Dict:
    """
    Evaluate a code generation method on HumanEval problems.

    Returns dict with:
    - pass_at_1: pass@1 rate
    - pass_at_k: pass@k rate (k=num_samples)
    - fpc: First-Pass Correctness
    - avg_time: Average generation time
    - per_problem_results: list of per-problem dicts
    """
    results = []
    total_pass = 0
    total_time = 0.0

    for i, prob in enumerate(problems):
        problem_id = prob["task_id"]
        prompt = prob["prompt"]
        test = prob["test"]
        entry_point = prob["entry_point"]
        canonical = prob["canonical_solution"]

        if verbose:
            print(f"  [{i+1}/{len(problems)}] {problem_id}: {entry_point}")

        problem_results = {
            "problem_id": problem_id,
            "entry_point": entry_point,
            "passed": False,
            "samples_passed": 0,
            "time": 0.0,
        }

        start = time.time()
        samples_passed = 0

        def timeout_handler(signum, frame):
            raise TimeoutError("Problem timeout")

        try:
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(60)  # 60-second per-problem timeout

            try:
                # Generate num_samples completions
                generated_codes = generate_fn(prompt, problem_id, entry_point)
                if isinstance(generated_codes, str):
                    generated_codes = [generated_codes]

                for code in generated_codes:
                    # Try multiple strategies to get valid executable code
                    # Strategy 1: Use code as-is (already includes prompt+generation)
                    passed = run_humaneval_test(code, test, entry_point)
                    if passed:
                        samples_passed += 1
                        continue

                    # Strategy 2: prompt + code (if code is completion only)
                    if not passed and not code.startswith("def "):
                        full = prompt + code
                        passed = run_humaneval_test(full, test, entry_point)
                        if passed:
                            samples_passed += 1
                            continue

                    # Strategy 3: Extract function body
                    if not passed:
                        func_code = extract_function_body(code, prompt, entry_point)
                        passed = run_humaneval_test(func_code, test, entry_point)
                        if passed:
                            samples_passed += 1
            except TimeoutError:
                if verbose:
                    print(f"    Timeout!")
            finally:
                signal.signal(signal.SIGALRM, old_handler)
                signal.alarm(0)

        except Exception as e:
            if verbose:
                print(f"    Error: {e}")

        elapsed = time.time() - start
        total_time += elapsed

        passed_any = samples_passed > 0
        if passed_any:
            total_pass += 1

        problem_results["passed"] = passed_any
        problem_results["samples_passed"] = samples_passed
        problem_results["time"] = elapsed
        results.append(problem_results)

        if verbose:
            status = "PASS" if passed_any else "FAIL"
            print(f"    {status} (time={elapsed:.1f}s)")

    n_problems = len(problems)
    pass_at_1 = total_pass / n_problems if n_problems > 0 else 0.0
    avg_time = total_time / n_problems if n_problems > 0 else 0.0

    return {
        "method": method_name,
        "pass_at_1": pass_at_1,
        "fpc": pass_at_1,  # First-pass correctness = pass@1 for single-shot
        "avg_time": avg_time,
        "total_pass": total_pass,
        "total_problems": n_problems,
        "per_problem_results": results,
    }


def compute_specification_compliance_rate(
    results: List[Dict],
    problems: list,
) -> float:
    """
    Compute Specification Compliance Rate (SCR):
    Fraction of generated programs passing SMT checks.
    """
    from spec_augment import check_smt_consistency

    compliant = 0
    total = 0

    for result, prob in zip(results, problems):
        problem_id = prob["task_id"]
        if result.get("generated_code"):
            smt_score = check_smt_consistency(result["generated_code"], problem_id)
            if smt_score >= 0.7:  # Threshold for compliance
                compliant += 1
            total += 1

    return compliant / total if total > 0 else 0.0
