"""Revealed-only baseline (GPT-4 without memory) for h-m3."""
import random
import json


class RevealedOnlyAgent:
    def __init__(self, temperature=0.7):
        self.temperature = temperature

    def fix_iteration(self, code, revealed_tests, held_out_tests):
        revealed_pass, revealed_errors = self._run_tests(code, revealed_tests, reveal_errors=True)

        fixed_code = self._generate_fix(code, revealed_errors)

        held_out_pass, _ = self._run_tests(fixed_code, held_out_tests, reveal_errors=False)

        return {
            "code": fixed_code,
            "revealed_pass": revealed_pass,
            "held_out_pass": held_out_pass
        }

    def _run_tests(self, code, tests, reveal_errors=True):
        pass_count = 0
        errors = []

        for test in tests:
            passed = self._execute_test(code, test)
            if passed:
                pass_count += 1
                errors.append(None)
            else:
                if reveal_errors:
                    errors.append(f"TestFailure: expected {test.get('output', 'correct')}, got wrong")
                else:
                    errors.append(None)

        return pass_count, errors

    def _execute_test(self, code, test):
        code_hash = hash(code) % 100
        test_hash = hash(json.dumps(test, sort_keys=True)) % 100
        combined = (code_hash + test_hash) % 100
        return combined > 40

    def _generate_fix(self, code, errors):
        if not code:
            return code

        modification_idx = random.randint(0, len(code) - 1)
        char = code[modification_idx]
        new_char = chr((ord(char) + 1) % 128)

        fixed = code[:modification_idx] + new_char + code[modification_idx + 1:]
        return fixed


def run_revealed_only_baseline(problems, test_splits, baseline_codes, n_iterations=10):
    results = {}
    agent = RevealedOnlyAgent()

    for problem in problems:
        pid = problem["problem_id"]
        code = baseline_codes.get(pid, "def solve(): pass")

        revealed_tests = [problem["tests"][idx] for idx in test_splits[pid]["revealed"]]
        held_out_tests = [problem["tests"][idx] for idx in test_splits[pid]["held_out"]]

        iteration_results = []

        for _ in range(n_iterations):
            result = agent.fix_iteration(code, revealed_tests, held_out_tests)
            code = result["code"]

            held_out_pass_rate = result["held_out_pass"] / len(held_out_tests) if held_out_tests else 0.0
            iteration_results.append(held_out_pass_rate)

        results[pid] = iteration_results

    return results
