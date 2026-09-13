"""
Data Loader Module for ExePlay Experiment
Loads and processes code generation datasets
"""
import json
from typing import List, Dict, Any, Optional
from datasets import load_dataset
import random


def load_mbpp_subset(num_samples: int = 50, split: str = "test") -> List[Dict[str, Any]]:
    """
    Load a subset of MBPP (Mostly Basic Python Problems) dataset.

    Args:
        num_samples: Number of samples to load
        split: Dataset split to use

    Returns:
        List of task dictionaries with problem, test cases, and reference solution
    """
    dataset = load_dataset("google-research-datasets/mbpp", "full", split=split)

    tasks = []
    for i, item in enumerate(dataset):
        if i >= num_samples:
            break

        # Parse test cases from the assertion strings
        test_cases = []
        for assertion in item.get('test_list', []):
            # Parse assertion like "assert func(x) == y"
            try:
                test_cases.append({
                    'assertion': assertion,
                    'raw': assertion
                })
            except:
                continue

        task = {
            'id': item.get('task_id', i),
            'problem': item.get('text', ''),
            'prompt': item.get('prompt', item.get('text', '')),
            'reference_solution': item.get('code', ''),
            'test_cases': test_cases,
            'test_list': item.get('test_list', []),
            'entry_point': None  # MBPP doesn't specify entry points
        }
        tasks.append(task)

    return tasks


def load_humaneval_subset(num_samples: int = 50) -> List[Dict[str, Any]]:
    """
    Load a subset of HumanEval dataset.

    Args:
        num_samples: Number of samples to load

    Returns:
        List of task dictionaries
    """
    dataset = load_dataset("openai/openai_humaneval", split="test")

    tasks = []
    for i, item in enumerate(dataset):
        if i >= num_samples:
            break

        task = {
            'id': item.get('task_id', f'HumanEval/{i}'),
            'problem': item.get('prompt', ''),
            'prompt': item.get('prompt', ''),
            'reference_solution': item.get('canonical_solution', ''),
            'test_code': item.get('test', ''),
            'entry_point': item.get('entry_point', None),
        }
        tasks.append(task)

    return tasks


def create_synthetic_tasks(num_tasks: int = 20) -> List[Dict[str, Any]]:
    """
    Create synthetic code generation tasks for testing.

    Args:
        num_tasks: Number of tasks to create

    Returns:
        List of task dictionaries
    """
    task_templates = [
        {
            'problem': 'Write a function that returns the sum of two numbers.',
            'prompt': 'def add(a, b):',
            'reference_solution': 'def add(a, b):\n    return a + b',
            'test_cases': [
                {'input': (1, 2), 'expected_output': 3},
                {'input': (0, 0), 'expected_output': 0},
                {'input': (-1, 1), 'expected_output': 0},
            ],
            'entry_point': 'add'
        },
        {
            'problem': 'Write a function that returns the factorial of a number.',
            'prompt': 'def factorial(n):',
            'reference_solution': 'def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)',
            'test_cases': [
                {'input': 5, 'expected_output': 120},
                {'input': 0, 'expected_output': 1},
                {'input': 1, 'expected_output': 1},
            ],
            'entry_point': 'factorial'
        },
        {
            'problem': 'Write a function that checks if a number is prime.',
            'prompt': 'def is_prime(n):',
            'reference_solution': 'def is_prime(n):\n    if n < 2:\n        return False\n    for i in range(2, int(n**0.5) + 1):\n        if n % i == 0:\n            return False\n    return True',
            'test_cases': [
                {'input': 7, 'expected_output': True},
                {'input': 4, 'expected_output': False},
                {'input': 2, 'expected_output': True},
            ],
            'entry_point': 'is_prime'
        },
        {
            'problem': 'Write a function that reverses a string.',
            'prompt': 'def reverse_string(s):',
            'reference_solution': 'def reverse_string(s):\n    return s[::-1]',
            'test_cases': [
                {'input': 'hello', 'expected_output': 'olleh'},
                {'input': '', 'expected_output': ''},
                {'input': 'a', 'expected_output': 'a'},
            ],
            'entry_point': 'reverse_string'
        },
        {
            'problem': 'Write a function that returns the maximum value in a list.',
            'prompt': 'def find_max(lst):',
            'reference_solution': 'def find_max(lst):\n    if not lst:\n        return None\n    return max(lst)',
            'test_cases': [
                {'input': [1, 2, 3, 4, 5], 'expected_output': 5},
                {'input': [-1, -2, -3], 'expected_output': -1},
                {'input': [42], 'expected_output': 42},
            ],
            'entry_point': 'find_max'
        },
        {
            'problem': 'Write a function that counts the number of vowels in a string.',
            'prompt': 'def count_vowels(s):',
            'reference_solution': 'def count_vowels(s):\n    return sum(1 for c in s.lower() if c in "aeiou")',
            'test_cases': [
                {'input': 'hello', 'expected_output': 2},
                {'input': 'xyz', 'expected_output': 0},
                {'input': 'AEIOU', 'expected_output': 5},
            ],
            'entry_point': 'count_vowels'
        },
        {
            'problem': 'Write a function that returns the nth Fibonacci number.',
            'prompt': 'def fibonacci(n):',
            'reference_solution': 'def fibonacci(n):\n    if n <= 1:\n        return n\n    a, b = 0, 1\n    for _ in range(2, n + 1):\n        a, b = b, a + b\n    return b',
            'test_cases': [
                {'input': 0, 'expected_output': 0},
                {'input': 1, 'expected_output': 1},
                {'input': 10, 'expected_output': 55},
            ],
            'entry_point': 'fibonacci'
        },
        {
            'problem': 'Write a function that checks if a string is a palindrome.',
            'prompt': 'def is_palindrome(s):',
            'reference_solution': 'def is_palindrome(s):\n    s = s.lower()\n    return s == s[::-1]',
            'test_cases': [
                {'input': 'radar', 'expected_output': True},
                {'input': 'hello', 'expected_output': False},
                {'input': '', 'expected_output': True},
            ],
            'entry_point': 'is_palindrome'
        },
        {
            'problem': 'Write a function that returns all even numbers from a list.',
            'prompt': 'def get_evens(lst):',
            'reference_solution': 'def get_evens(lst):\n    return [x for x in lst if x % 2 == 0]',
            'test_cases': [
                {'input': [1, 2, 3, 4, 5, 6], 'expected_output': [2, 4, 6]},
                {'input': [1, 3, 5], 'expected_output': []},
                {'input': [], 'expected_output': []},
            ],
            'entry_point': 'get_evens'
        },
        {
            'problem': 'Write a function that calculates the power of a number.',
            'prompt': 'def power(base, exp):',
            'reference_solution': 'def power(base, exp):\n    return base ** exp',
            'test_cases': [
                {'input': (2, 3), 'expected_output': 8},
                {'input': (5, 0), 'expected_output': 1},
                {'input': (3, 2), 'expected_output': 9},
            ],
            'entry_point': 'power'
        },
    ]

    tasks = []
    for i in range(num_tasks):
        template = task_templates[i % len(task_templates)]
        task = {
            'id': f'synthetic_{i}',
            'problem': template['problem'],
            'prompt': template['prompt'],
            'reference_solution': template['reference_solution'],
            'test_cases': template['test_cases'],
            'entry_point': template['entry_point']
        }
        tasks.append(task)

    return tasks


def prepare_dataset(dataset_name: str = "mbpp", num_samples: int = 50) -> List[Dict[str, Any]]:
    """
    Prepare dataset for the experiment.

    Args:
        dataset_name: Name of the dataset ('mbpp', 'humaneval', or 'synthetic')
        num_samples: Number of samples to load

    Returns:
        List of task dictionaries
    """
    if dataset_name == "mbpp":
        return load_mbpp_subset(num_samples)
    elif dataset_name == "humaneval":
        return load_humaneval_subset(num_samples)
    else:
        return create_synthetic_tasks(num_samples)
