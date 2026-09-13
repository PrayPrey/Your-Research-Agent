"""
Programming tasks for evaluation.
"""

# A collection of programming tasks with test cases
PROGRAMMING_TASKS = [
    {
        "id": 1,
        "description": "Write a function that returns the sum of all even numbers in a list.",
        "function_name": "sum_even_numbers",
        "test_cases": [
            {"input": [[1, 2, 3, 4, 5, 6]], "expected": 12},
            {"input": [[2, 4, 6, 8]], "expected": 20},
            {"input": [[1, 3, 5]], "expected": 0},
            {"input": [[]], "expected": 0},
            {"input": [[-2, -4, 3, 5]], "expected": -6},
        ]
    },
    {
        "id": 2,
        "description": "Write a function that checks if a string is a palindrome (case-insensitive).",
        "function_name": "is_palindrome",
        "test_cases": [
            {"input": ["racecar"], "expected": True},
            {"input": ["RaceCar"], "expected": True},
            {"input": ["hello"], "expected": False},
            {"input": ["A"], "expected": True},
            {"input": [""], "expected": True},
        ]
    },
    {
        "id": 3,
        "description": "Write a function that finds the maximum element in a list. Return None if the list is empty.",
        "function_name": "find_max",
        "test_cases": [
            {"input": [[1, 5, 3, 9, 2]], "expected": 9},
            {"input": [[-1, -5, -3]], "expected": -1},
            {"input": [[42]], "expected": 42},
            {"input": [[]], "expected": None},
            {"input": [[0, 0, 0]], "expected": 0},
        ]
    },
    {
        "id": 4,
        "description": "Write a function that reverses a list without using built-in reverse methods.",
        "function_name": "reverse_list",
        "test_cases": [
            {"input": [[1, 2, 3, 4, 5]], "expected": [5, 4, 3, 2, 1]},
            {"input": [[1]], "expected": [1]},
            {"input": [[]], "expected": []},
            {"input": [["a", "b", "c"]], "expected": ["c", "b", "a"]},
        ]
    },
    {
        "id": 5,
        "description": "Write a function that counts the occurrences of each character in a string and returns a dictionary.",
        "function_name": "count_characters",
        "test_cases": [
            {"input": ["hello"], "expected": {"h": 1, "e": 1, "l": 2, "o": 1}},
            {"input": ["aaa"], "expected": {"a": 3}},
            {"input": [""], "expected": {}},
            {"input": ["abcABC"], "expected": {"a": 1, "b": 1, "c": 1, "A": 1, "B": 1, "C": 1}},
        ]
    },
    {
        "id": 6,
        "description": "Write a function that removes duplicates from a list while preserving order.",
        "function_name": "remove_duplicates",
        "test_cases": [
            {"input": [[1, 2, 2, 3, 4, 4, 5]], "expected": [1, 2, 3, 4, 5]},
            {"input": [[1, 1, 1]], "expected": [1]},
            {"input": [[]], "expected": []},
            {"input": [[1, 2, 3]], "expected": [1, 2, 3]},
        ]
    },
    {
        "id": 7,
        "description": "Write a function that finds the nth Fibonacci number (0-indexed). Use iteration, not recursion.",
        "function_name": "fibonacci",
        "test_cases": [
            {"input": [0], "expected": 0},
            {"input": [1], "expected": 1},
            {"input": [5], "expected": 5},
            {"input": [10], "expected": 55},
            {"input": [15], "expected": 610},
        ]
    },
    {
        "id": 8,
        "description": "Write a function that checks if a number is prime.",
        "function_name": "is_prime",
        "test_cases": [
            {"input": [2], "expected": True},
            {"input": [17], "expected": True},
            {"input": [1], "expected": False},
            {"input": [4], "expected": False},
            {"input": [97], "expected": True},
        ]
    },
    {
        "id": 9,
        "description": "Write a function that merges two sorted lists into one sorted list.",
        "function_name": "merge_sorted_lists",
        "test_cases": [
            {"input": [[1, 3, 5], [2, 4, 6]], "expected": [1, 2, 3, 4, 5, 6]},
            {"input": [[1, 2, 3], [4, 5, 6]], "expected": [1, 2, 3, 4, 5, 6]},
            {"input": [[], [1, 2, 3]], "expected": [1, 2, 3]},
            {"input": [[1, 2, 3], []], "expected": [1, 2, 3]},
        ]
    },
    {
        "id": 10,
        "description": "Write a function that finds all pairs in a list that sum to a target value.",
        "function_name": "find_pairs_with_sum",
        "test_cases": [
            {"input": [[1, 2, 3, 4, 5], 5], "expected": [(1, 4), (2, 3)]},
            {"input": [[1, 1, 1, 1], 2], "expected": [(1, 1), (1, 1), (1, 1)]},
            {"input": [[1, 2, 3], 10], "expected": []},
            {"input": [[], 5], "expected": []},
        ]
    },
    {
        "id": 11,
        "description": "Write a function that rotates a list to the right by k positions.",
        "function_name": "rotate_list",
        "test_cases": [
            {"input": [[1, 2, 3, 4, 5], 2], "expected": [4, 5, 1, 2, 3]},
            {"input": [[1, 2, 3], 1], "expected": [3, 1, 2]},
            {"input": [[1, 2, 3], 0], "expected": [1, 2, 3]},
            {"input": [[1], 5], "expected": [1]},
        ]
    },
    {
        "id": 12,
        "description": "Write a function that checks if two strings are anagrams of each other (case-insensitive).",
        "function_name": "are_anagrams",
        "test_cases": [
            {"input": ["listen", "silent"], "expected": True},
            {"input": ["Hello", "Olelh"], "expected": True},
            {"input": ["abc", "def"], "expected": False},
            {"input": ["", ""], "expected": True},
        ]
    },
    {
        "id": 13,
        "description": "Write a function that finds the longest common prefix among a list of strings.",
        "function_name": "longest_common_prefix",
        "test_cases": [
            {"input": [["flower", "flow", "flight"]], "expected": "fl"},
            {"input": [["dog", "racecar", "car"]], "expected": ""},
            {"input": [["interspecies", "interstellar", "interstate"]], "expected": "inters"},
            {"input": [[]], "expected": ""},
        ]
    },
    {
        "id": 14,
        "description": "Write a function that converts a Roman numeral to an integer.",
        "function_name": "roman_to_int",
        "test_cases": [
            {"input": ["III"], "expected": 3},
            {"input": ["IV"], "expected": 4},
            {"input": ["IX"], "expected": 9},
            {"input": ["LVIII"], "expected": 58},
            {"input": ["MCMXCIV"], "expected": 1994},
        ]
    },
    {
        "id": 15,
        "description": "Write a function that finds the missing number in a list of integers from 0 to n.",
        "function_name": "find_missing_number",
        "test_cases": [
            {"input": [[0, 1, 3]], "expected": 2},
            {"input": [[0, 1, 2, 3, 4, 5, 7]], "expected": 6},
            {"input": [[1]], "expected": 0},
            {"input": [[0]], "expected": 1},
        ]
    },
    {
        "id": 16,
        "description": "Write a function that checks if a string has balanced parentheses.",
        "function_name": "is_balanced",
        "test_cases": [
            {"input": ["()"], "expected": True},
            {"input": ["()[]{}"], "expected": True},
            {"input": ["(]"], "expected": False},
            {"input": ["([)]"], "expected": False},
            {"input": ["{[]}"], "expected": True},
        ]
    },
    {
        "id": 17,
        "description": "Write a function that finds the first non-repeating character in a string. Return None if all characters repeat.",
        "function_name": "first_non_repeating",
        "test_cases": [
            {"input": ["leetcode"], "expected": "l"},
            {"input": ["loveleetcode"], "expected": "v"},
            {"input": ["aabb"], "expected": None},
            {"input": ["z"], "expected": "z"},
        ]
    },
    {
        "id": 18,
        "description": "Write a function that returns the power set (all subsets) of a list.",
        "function_name": "power_set",
        "test_cases": [
            {"input": [[1, 2]], "expected": [[], [1], [2], [1, 2]]},
            {"input": [[1]], "expected": [[], [1]]},
            {"input": [[]], "expected": [[]]},
        ]
    },
    {
        "id": 19,
        "description": "Write a function that performs binary search on a sorted list. Return the index if found, -1 otherwise.",
        "function_name": "binary_search",
        "test_cases": [
            {"input": [[1, 2, 3, 4, 5], 3], "expected": 2},
            {"input": [[1, 2, 3, 4, 5], 6], "expected": -1},
            {"input": [[1], 1], "expected": 0},
            {"input": [[], 1], "expected": -1},
        ]
    },
    {
        "id": 20,
        "description": "Write a function that flattens a nested list of arbitrary depth.",
        "function_name": "flatten_list",
        "test_cases": [
            {"input": [[[1, [2, [3, 4]], 5]]], "expected": [1, 2, 3, 4, 5]},
            {"input": [[[1, 2, 3]]], "expected": [1, 2, 3]},
            {"input": [[[[[1]]]]], "expected": [1]},
            {"input": [[[]]], "expected": []},
        ]
    },
]
