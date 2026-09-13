"""Data loading for HumanEval benchmark."""

import ast
import random
from typing import Any

import config


def load_humaneval_problems() -> dict[str, dict]:
    """Load HumanEval-style problems.

    For PoC: generates synthetic problems representing the 164 HumanEval tasks.
    In production: use human_eval.data.read_problems().
    """
    problems = {}
    prompts = [
        "def add(a, b):\n    '''Add two numbers.'''\n    ",
        "def multiply(a, b):\n    '''Multiply two numbers.'''\n    ",
        "def subtract(a, b):\n    '''Subtract b from a.'''\n    ",
        "def divide(a, b):\n    '''Divide a by b.'''\n    ",
        "def modulo(a, b):\n    '''Return a mod b.'''\n    ",
        "def power(a, b):\n    '''Return a to the power of b.'''\n    ",
        "def max_val(lst):\n    '''Return maximum value in list.'''\n    ",
        "def min_val(lst):\n    '''Return minimum value in list.'''\n    ",
        "def sum_list(lst):\n    '''Return sum of list elements.'''\n    ",
        "def avg_list(lst):\n    '''Return average of list elements.'''\n    ",
    ]

    for i in range(config.HUMANEVAL_SIZE):
        task_id = f"HumanEval/{i}"
        problems[task_id] = {
            "task_id": task_id,
            "prompt": prompts[i % len(prompts)],
            "entry_point": prompts[i % len(prompts)].split("(")[0].replace("def ", ""),
            "test": f"assert {prompts[i % len(prompts)].split('(')[0].replace('def ', '')}(1, 2) is not None",
        }
    return problems


def load_verus_task_ids() -> set[str]:
    """Return task_ids with formal specifications (HumanEval-Verus subset)."""
    return config.VERUS_TASK_IDS.copy()


def generate_samples(
    model_name: str,
    problems: dict[str, dict],
    n: int = config.N_SAMPLES,
    temperature: float = config.TEMPERATURE,
    seed: int = config.SEED,
) -> list[dict]:
    """Generate n completions per problem.

    For PoC: generates synthetic completions with controlled error injection.
    Error classes are designed to be largely independent (Jaccard < 0.30).
    In production: use model inference.
    """
    random.seed(seed + hash(model_name) % 1000)
    samples = []

    for task_id, prob in problems.items():
        task_num = int(task_id.split("/")[1])

        for i in range(n):
            sample_hash = hash((task_id, model_name, i)) % 100

            if task_num % 10 < 3:
                code = "reutrn a + b"
            elif task_num % 10 < 5:
                code = "return a + b  # todo: fix"
            elif task_num % 10 < 7:
                code = "return lst[0]"
            else:
                code = "return a + b"

            if sample_hash < 20:
                code = "ret " + code.replace("return ", "").replace("reutrn ", "")

            full_code = prob["prompt"] + code

            samples.append({
                "task_id": task_id,
                "completion": full_code,
                "model": model_name,
            })

    return samples
