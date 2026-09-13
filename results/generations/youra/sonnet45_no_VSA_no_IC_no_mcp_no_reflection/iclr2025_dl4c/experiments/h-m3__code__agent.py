"""Mock GPT-4 agent with pattern memory for h-m3."""
import random
import json
from pattern_memory import PatternMemory, Pattern


class MockGPT4Agent:
    def __init__(self, memory=None, temperature=0.7):
        self.memory = memory or PatternMemory()
        self.temperature = temperature

    def fix_iteration(self, problem, current_code, revealed_tests, held_out_tests):
        revealed_pass, revealed_errors = self._run_tests(current_code, revealed_tests, reveal_errors=True)

        patterns = []
        if revealed_errors and revealed_errors[0]:
            patterns = self.memory.retrieve_similar(
                current_error=revealed_errors[0],
                current_code=current_code,
                top_k=3
            )

        fixed_code = self._generate_fix(current_code, revealed_errors, patterns)

        pattern_extracted = None
        if revealed_errors and revealed_errors[0]:
            pattern_extracted = self._extract_pattern(revealed_errors[0], current_code, fixed_code)
            self.memory.store_pattern(
                error_type=pattern_extracted.error_type,
                code_region=pattern_extracted.code_region,
                fix_template=pattern_extracted.fix_template,
                problem_id=problem["problem_id"]
            )

        for p in patterns:
            self.memory.log_usage(p, used=True)

        held_out_pass, _ = self._run_tests(fixed_code, held_out_tests, reveal_errors=False)

        return {
            "code": fixed_code,
            "revealed_pass": revealed_pass,
            "held_out_pass": held_out_pass,
            "pattern_extracted": pattern_extracted,
            "patterns_used": patterns
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
                    errors.append(f"TestFailure: expected {test.get('output', 'correct')}, got wrong result")
                else:
                    errors.append(None)

        return pass_count, errors

    def _execute_test(self, code, test):
        code_hash = hash(code) % 100
        test_hash = hash(json.dumps(test, sort_keys=True)) % 100
        combined = (code_hash + test_hash) % 100
        return combined > 40

    def _generate_fix(self, code, errors, patterns):
        if patterns and random.random() < 0.7:
            fix_boost = 0.15
        else:
            fix_boost = 0.05

        modification_idx = random.randint(0, len(code) - 1)
        char = code[modification_idx]
        new_char = chr((ord(char) + 1) % 128)

        fixed = code[:modification_idx] + new_char + code[modification_idx + 1:]
        return fixed

    def _extract_pattern(self, error_msg, code, fix):
        error_type = "IndexError" if "index" in error_msg.lower() else "TypeError"
        code_region = "loop bounds" if "for" in code or "while" in code else "function call"
        fix_template = "Check boundary conditions before access"

        return Pattern(
            error_type=error_type,
            code_region=code_region,
            fix_template=fix_template,
            problem_id="",
            success_count=0
        )


def run_tests(code, tests, reveal_errors=True):
    agent = MockGPT4Agent()
    return agent._run_tests(code, tests, reveal_errors)
