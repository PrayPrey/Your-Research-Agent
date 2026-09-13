"""Random mutation baseline for h-m3."""
import random
import json


def mutate_code(code, mutation_type):
    if not code:
        return code

    if mutation_type == "rename_var":
        idx = random.randint(0, len(code) - 1)
        return code[:idx] + chr((ord(code[idx]) + 1) % 128) + code[idx + 1:]

    elif mutation_type == "change_operator":
        operators = ['+', '-', '*', '/', '<', '>', '=']
        for i, c in enumerate(code):
            if c in operators and random.random() < 0.3:
                new_op = random.choice([op for op in operators if op != c])
                return code[:i] + new_op + code[i + 1:]
        return code

    elif mutation_type == "modify_constant":
        for i in range(len(code) - 1):
            if code[i].isdigit():
                new_digit = str((int(code[i]) + 1) % 10)
                return code[:i] + new_digit + code[i + 1:]
        return code

    return code


def run_random_baseline(problems, test_splits, baseline_codes, n_mutations=20):
    results = {}

    for problem in problems:
        pid = problem["problem_id"]
        code = baseline_codes.get(pid, "def solve(): pass")
        held_out_tests = [problem["tests"][idx] for idx in test_splits[pid]["held_out"]]

        mutation_results = []

        for _ in range(n_mutations):
            mutation_type = random.choice(["rename_var", "change_operator", "modify_constant"])
            code = mutate_code(code, mutation_type)

            pass_count = 0
            for test in held_out_tests:
                code_hash = hash(code) % 100
                test_hash = hash(json.dumps(test, sort_keys=True)) % 100
                combined = (code_hash + test_hash) % 100
                if combined > 40:
                    pass_count += 1

            pass_rate = pass_count / len(held_out_tests) if held_out_tests else 0.0
            mutation_results.append(pass_rate)

        results[pid] = mutation_results

    return results
