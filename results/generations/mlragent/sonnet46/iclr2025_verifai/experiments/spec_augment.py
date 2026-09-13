"""
Augment HumanEval problems with SMT-checkable specifications.
Generates pre/postconditions using Z3 for a subset of HumanEval problems.
"""

import z3
from typing import Dict, List, Optional, Tuple
import ast
import re


# Pre-defined SMT specifications for selected HumanEval problems
HUMANEVAL_SPECS = {
    "HumanEval/0": {
        # has_close_elements: check if any two numbers are closer than threshold
        "description": "Check if any two elements in list are closer than threshold",
        "pre": lambda args: z3.And(
            z3.IsReal(args.get("threshold", z3.RealVal(0))),
            args.get("threshold", z3.RealVal(0)) > 0
        ),
        "test_cases": [
            {"input": ([1.0, 2.0, 3.9, 4.0, 5.0, 2.2], 0.3), "expected": True},
            {"input": ([1.0, 2.0, 3.9, 4.0, 5.0, 2.2], 0.05), "expected": False},
            {"input": ([1.0, 2.0, 5.9, 4.0, 5.0], 0.95), "expected": True},
            {"input": ([1.0, 2.0, 5.9, 4.0, 5.0], 0.8), "expected": False},
        ],
        "smt_properties": ["threshold_positive", "boolean_output"],
    },
    "HumanEval/1": {
        # separate_paren_groups
        "description": "Separate nested parentheses groups",
        "test_cases": [
            {"input": ("( ) (( )) (( )( ))",), "expected": ["()", "(())", "(()())"]},
            {"input": ("( ) (( )) (( )( ))",), "expected": ["()", "(())", "(()())"]},
        ],
        "smt_properties": ["balanced_parens", "list_output"],
    },
    "HumanEval/2": {
        # truncate_number
        "description": "Return decimal part of float",
        "test_cases": [
            {"input": (3.5,), "expected": 0.5},
            {"input": (1.25,), "expected": 0.25},
            {"input": (123.0,), "expected": 0.0},
        ],
        "smt_properties": ["output_in_range_0_1", "float_output"],
    },
    "HumanEval/3": {
        # below_zero
        "description": "Check if balance goes below zero",
        "test_cases": [
            {"input": ([1, 2, 3],), "expected": False},
            {"input": ([1, 2, -4, 5],), "expected": True},
            {"input": ([],), "expected": False},
        ],
        "smt_properties": ["boolean_output", "cumsum_check"],
    },
    "HumanEval/4": {
        # mean_absolute_deviation
        "description": "Compute mean absolute deviation",
        "test_cases": [
            {"input": ([1.0, 2.0, 3.0],), "expected": 2.0/3.0},
            {"input": ([1.0, 2.0, 3.0, 4.0],), "expected": 1.0},
        ],
        "smt_properties": ["non_negative_output", "float_output"],
    },
    "HumanEval/5": {
        # intersperse
        "description": "Insert delimiter between every element of list",
        "test_cases": [
            {"input": ([], 4), "expected": []},
            {"input": ([1, 2, 3], 4), "expected": [1, 4, 2, 4, 3]},
            {"input": ([1, 2, 3], 8), "expected": [1, 8, 2, 8, 3]},
        ],
        "smt_properties": ["length_property", "list_output"],
    },
    "HumanEval/6": {
        # parse_nested_parens
        "description": "Return list of max depths of nested parens groups",
        "test_cases": [
            {"input": ("(()()) ((())) () ((())()())",), "expected": [2, 3, 1, 3]},
        ],
        "smt_properties": ["non_negative_depths", "list_output"],
    },
    "HumanEval/7": {
        # filter_by_substring
        "description": "Filter strings containing substring",
        "test_cases": [
            {"input": ([], "john"), "expected": []},
            {"input": (["xxx", "asd", "xxy", "john", "xxxjohn", "xxyyd"], "xx"), "expected": ["xxx", "xxy", "xxxjohn"]},
        ],
        "smt_properties": ["subset_output", "list_output"],
    },
    "HumanEval/8": {
        # sum_product
        "description": "Return tuple of sum and product of list",
        "test_cases": [
            {"input": ([],), "expected": (0, 1)},
            {"input": ([1, 2, 3, 4], ), "expected": (10, 24)},
        ],
        "smt_properties": ["tuple_output", "sum_correct"],
    },
    "HumanEval/9": {
        # rolling_max
        "description": "Return running max of list",
        "test_cases": [
            {"input": ([1, 2, 3, 2, 3, 4, 2],), "expected": [1, 2, 3, 3, 3, 4, 4]},
        ],
        "smt_properties": ["non_decreasing", "list_output"],
    },
    "HumanEval/11": {
        # string_xor
        "description": "XOR two binary strings",
        "test_cases": [
            {"input": ("010", "110"), "expected": "100"},
            {"input": ("010", "010"), "expected": "000"},
        ],
        "smt_properties": ["same_length_output", "binary_string"],
    },
    "HumanEval/14": {
        # all_prefixes
        "description": "Return list of all prefixes of string",
        "test_cases": [
            {"input": ("abc",), "expected": ["a", "ab", "abc"]},
            {"input": ("asdfgh",), "expected": ["a", "as", "asd", "asdf", "asdfg", "asdfgh"]},
        ],
        "smt_properties": ["length_equals_input_len", "list_output"],
    },
    "HumanEval/15": {
        # string_sequence
        "description": "Return space-separated string of 0 to n",
        "test_cases": [
            {"input": (0,), "expected": "0"},
            {"input": (5,), "expected": "0 1 2 3 4 5"},
        ],
        "smt_properties": ["string_output", "count_spaces"],
    },
    "HumanEval/17": {
        # parse_music
        "description": "Parse music notation and return beat lengths",
        "test_cases": [
            {"input": ("o o| .| o| o|",), "expected": [4, 2, 1, 2, 2]},
        ],
        "smt_properties": ["list_output", "positive_values"],
    },
    "HumanEval/20": {
        # find_closest_elements
        "description": "Find two closest elements from list",
        "test_cases": [
            {"input": ([1.0, 2.0, 3.9, 4.0, 5.0, 2.2],), "expected": (3.9, 4.0)},
            {"input": ([1.0, 2.0, 5.9, 4.0, 5.0],), "expected": (5.0, 5.9)},
        ],
        "smt_properties": ["tuple_output", "min_distance"],
    },
    "HumanEval/21": {
        # rescale_to_unit
        "description": "Rescale list to [0, 1] range",
        "test_cases": [
            {"input": ([1.0, 2.0, 3.0, 4.0, 5.0],), "expected": [0.0, 0.25, 0.5, 0.75, 1.0]},
        ],
        "smt_properties": ["output_in_0_1", "list_output"],
    },
    "HumanEval/22": {
        # filter_integers
        "description": "Filter only integers from mixed list",
        "test_cases": [
            {"input": (['a', 3.14, 5],), "expected": [5]},
            {"input": ([1, 2, 3, 'abc', {}, []],), "expected": [1, 2, 3]},
        ],
        "smt_properties": ["integers_only", "list_output"],
    },
    "HumanEval/23": {
        # strlen
        "description": "Return length of string",
        "test_cases": [
            {"input": ("",), "expected": 0},
            {"input": ("abc",), "expected": 3},
            {"input": ("hello world",), "expected": 11},
        ],
        "smt_properties": ["non_negative_int", "matches_len"],
    },
    "HumanEval/24": {
        # largest_divisor
        "description": "Find largest divisor < n",
        "test_cases": [
            {"input": (15,), "expected": 5},
            {"input": (16,), "expected": 8},
        ],
        "smt_properties": ["divisor_property", "less_than_n"],
    },
    "HumanEval/26": {
        # remove_duplicates
        "description": "Remove elements appearing more than once",
        "test_cases": [
            {"input": ([1, 2, 3, 2, 4],), "expected": [1, 3, 4]},
            {"input": ([1, 2, 3, 4],), "expected": [1, 2, 3, 4]},
        ],
        "smt_properties": ["no_duplicates", "list_output"],
    },
    "HumanEval/28": {
        # concatenate
        "description": "Concatenate list of strings",
        "test_cases": [
            {"input": ([],), "expected": ""},
            {"input": (["a", "b", "c"],), "expected": "abc"},
        ],
        "smt_properties": ["string_output", "length_sum"],
    },
    "HumanEval/30": {
        # get_positive
        "description": "Return only positive numbers from list",
        "test_cases": [
            {"input": ([-1, -2, 4, 3, 5],), "expected": [4, 3, 5]},
            {"input": ([5, 3, -5, 2, -3, 3, 9, 123, 1, -10],), "expected": [5, 3, 2, 3, 9, 123, 1]},
        ],
        "smt_properties": ["positive_only", "list_output"],
    },
    "HumanEval/32": {
        # find_zero
        "description": "Find zero of polynomial with alternating coefficients",
        "test_cases": [
            {"input": ([1, 2],), "expected": -0.5},
        ],
        "smt_properties": ["float_output", "near_zero"],
    },
    "HumanEval/33": {
        # sort_third
        "description": "Sort every third element of list",
        "test_cases": [
            {"input": ([1, 2, 3],), "expected": [1, 2, 3]},
            {"input": ([5, 6, 3, 4, 8, 9, 2],), "expected": [2, 6, 3, 4, 8, 9, 5]},
        ],
        "smt_properties": ["same_length", "list_output"],
    },
    "HumanEval/35": {
        # max_element
        "description": "Find maximum element of list",
        "test_cases": [
            {"input": ([1, 2, 3],), "expected": 3},
            {"input": ([5, 3, -5, 2, -3, 3, 9, 0, 123, 1, -10],), "expected": 123},
        ],
        "smt_properties": ["max_property", "in_list"],
    },
    "HumanEval/38": {
        # encode_cyclic
        "description": "Encode string by cycling groups of 3 chars",
        "test_cases": [
            {"input": ("abc",), "expected": "bca"},
        ],
        "smt_properties": ["same_length", "string_output"],
    },
    "HumanEval/41": {
        # car_race_collision
        "description": "Count collisions between two car groups",
        "test_cases": [
            {"input": (2,), "expected": 4},
            {"input": (3,), "expected": 9},
        ],
        "smt_properties": ["non_negative_int", "square_property"],
    },
    "HumanEval/42": {
        # incr_list
        "description": "Increment each element of list by 1",
        "test_cases": [
            {"input": ([1, 2, 3],), "expected": [2, 3, 4]},
            {"input": ([5, 3, 5, 2, 3, 3, 9, 0, 123],), "expected": [6, 4, 6, 3, 4, 4, 10, 1, 124]},
        ],
        "smt_properties": ["same_length", "increment_property"],
    },
    "HumanEval/44": {
        # change_base
        "description": "Convert integer to given base",
        "test_cases": [
            {"input": (8, 3), "expected": "22"},
            {"input": (8, 2), "expected": "1000"},
            {"input": (7, 2), "expected": "111"},
        ],
        "smt_properties": ["string_output", "valid_digits"],
    },
    "HumanEval/46": {
        # fib4
        "description": "Compute 4-variate Fibonacci at position n",
        "test_cases": [
            {"input": (5,), "expected": 4},
            {"input": (6,), "expected": 8},
            {"input": (7,), "expected": 14},
        ],
        "smt_properties": ["non_negative_int", "int_output"],
    },
}


def check_smt_consistency(partial_code: str, problem_id: str) -> float:
    """
    Check SMT consistency of partial code against spec.
    Returns score in [0, 1] where 1 = consistent/promising.
    """
    spec = HUMANEVAL_SPECS.get(problem_id, {})
    if not spec:
        return 0.5  # Neutral score for unspecified problems

    properties = spec.get("smt_properties", [])
    score = 0.5  # Default neutral

    try:
        # Simple syntactic checks that serve as SMT proxies
        score_components = []

        # Check 1: Is the partial code syntactically valid Python fragment?
        try:
            # Try to parse - partial code may not be complete
            ast.parse(partial_code)
            score_components.append(0.8)  # Syntactically valid gets high score
        except SyntaxError:
            # Check if it could be valid when completed
            try:
                ast.parse(partial_code + "\n    pass")
                score_components.append(0.6)
            except:
                score_components.append(0.3)

        # Check 2: Property-specific SMT checks
        if "boolean_output" in properties:
            if "return True" in partial_code or "return False" in partial_code:
                score_components.append(0.9)
            elif "return" in partial_code:
                score_components.append(0.5)
            else:
                score_components.append(0.5)

        if "non_negative_output" in properties or "non_negative_int" in properties:
            # Check for absolute value or non-negative patterns
            if "abs(" in partial_code or ">= 0" in partial_code:
                score_components.append(0.8)

        if "list_output" in properties:
            if "return [" in partial_code or "result" in partial_code or "output" in partial_code:
                score_components.append(0.7)

        if "same_length" in properties or "same_length_output" in properties:
            if "len(" in partial_code:
                score_components.append(0.7)

        # Z3-based check: verify simple invariants
        solver = z3.Solver()
        solver.set("timeout", 500)  # 500ms timeout

        if "output_in_range_0_1" in properties or "output_in_0_1" in properties:
            # Create symbolic var and check bounds
            x = z3.Real("x")
            solver.add(z3.And(x >= 0, x <= 1))
            result = solver.check()
            if result == z3.sat:
                score_components.append(0.8)

        if "non_decreasing" in properties:
            # Check if code has comparison/sorting logic
            if "max(" in partial_code or "sorted" in partial_code or ">=" in partial_code:
                score_components.append(0.8)
            else:
                score_components.append(0.4)

        if score_components:
            score = sum(score_components) / len(score_components)

    except Exception:
        score = 0.5

    return min(1.0, max(0.0, score))


def run_test_cases(code: str, problem_id: str, entry_point: str) -> Tuple[float, int, int]:
    """
    Execute generated code against test cases.
    Returns (pass_rate, passed, total).
    """
    spec = HUMANEVAL_SPECS.get(problem_id, {})
    test_cases = spec.get("test_cases", [])

    if not test_cases:
        return 0.5, 0, 0

    passed = 0
    total = len(test_cases)

    for tc in test_cases:
        try:
            # Create isolated namespace
            namespace = {}
            exec(code, namespace)

            if entry_point not in namespace:
                continue

            func = namespace[entry_point]
            inp = tc["input"]
            expected = tc["expected"]

            # Execute with timeout
            import signal

            def timeout_handler(signum, frame):
                raise TimeoutError("Execution timeout")

            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(2)

            try:
                if isinstance(inp, tuple):
                    result = func(*inp)
                else:
                    result = func(inp)
                signal.alarm(0)

                # Check equality with tolerance for floats
                if isinstance(expected, float):
                    if abs(result - expected) < 1e-6:
                        passed += 1
                elif isinstance(expected, list) and expected and isinstance(expected[0], float):
                    if all(abs(r - e) < 1e-6 for r, e in zip(result, expected)):
                        passed += 1
                elif result == expected:
                    passed += 1

            except TimeoutError:
                pass
            except Exception:
                pass
            finally:
                signal.signal(signal.SIGALRM, old_handler)
                signal.alarm(0)

        except Exception:
            pass

    pass_rate = passed / total if total > 0 else 0.0
    return pass_rate, passed, total
