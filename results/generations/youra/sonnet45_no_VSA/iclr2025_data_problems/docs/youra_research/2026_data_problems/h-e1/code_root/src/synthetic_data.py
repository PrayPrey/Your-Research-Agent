"""Generate synthetic Python code with varying structural coupling for testing."""

import random
from typing import Dict, List


def generate_simple_solution(problem_id: str, variation: int) -> Dict[str, str]:
    """Generate a simple single-file Python solution."""
    num_imports = random.randint(0, 5)
    num_functions = random.randint(2, 8)
    num_classes = random.randint(0, 2)

    imports = []
    if num_imports > 0:
        available_imports = ["os", "sys", "math", "random", "json", "re", "collections", "itertools"]
        imports = random.sample(available_imports, min(num_imports, len(available_imports)))

    code = "#!/usr/bin/env python3\n\n"

    # Add imports
    for imp in imports:
        code += f"import {imp}\n"

    if imports:
        code += "\n"

    # Add utility functions
    for i in range(num_functions):
        func_name = f"func_{i}"
        # Randomly call other functions to create coupling
        calls = []
        if i > 0 and random.random() > 0.5:
            target = random.randint(0, i-1)
            calls.append(f"func_{target}()")

        code += f"def {func_name}(x):\n"
        code += f"    \"\"\"Function {i}.\"\"\"\n"
        for call in calls:
            code += f"    result = {call}\n"
        code += f"    return x * {i+1}\n\n"

    # Add classes
    for i in range(num_classes):
        class_name = f"Class{i}"
        code += f"class {class_name}:\n"
        code += f"    def __init__(self):\n"
        code += f"        self.value = {i}\n\n"
        code += f"    def method(self):\n"
        code += f"        return self.value * 2\n\n"

    # Add main function
    code += "def main():\n"
    code += f"    \"\"\"Main solution for problem {problem_id}.\"\"\"\n"
    code += "    n = int(input())\n"
    for i in range(min(3, num_functions)):
        code += f"    result_{i} = func_{i}(n)\n"
    code += "    print(sum([result_0"
    for i in range(1, min(3, num_functions)):
        code += f", result_{i}"
    code += "]))\n\n"

    code += "if __name__ == '__main__':\n"
    code += "    main()\n"

    return {
        "code": code,
        "problem": problem_id,
        "id": f"{problem_id}_sub_{variation}",
    }


def generate_synthetic_dataset(num_problems: int = 100, submissions_per_problem: int = 20) -> Dict[str, List[Dict]]:
    """Generate synthetic dataset with multiple solutions per problem."""
    dataset = {}

    for problem_id in range(num_problems):
        problem_name = f"problem_{problem_id:03d}"
        submissions = []

        for variation in range(submissions_per_problem):
            submission = generate_simple_solution(problem_name, variation)
            submissions.append(submission)

        dataset[problem_name] = submissions

    return dataset
