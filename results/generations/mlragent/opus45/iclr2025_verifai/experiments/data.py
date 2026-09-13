"""Dataset creation for SpecBridge experiments.

Creates a benchmark dataset with:
- Natural language requirements
- Ground truth formal specifications (pre/post conditions)
- Reference implementations
- Test cases
"""

BENCHMARK_PROBLEMS = [
    {
        "id": "p1",
        "name": "find_max",
        "description": "Write a function that finds the maximum element in a non-empty list of integers.",
        "specification": {
            "precondition": "len(arr) > 0 and all(isinstance(x, int) for x in arr)",
            "postcondition": "result == max(arr) and result in arr",
            "invariants": []
        },
        "test_cases": [
            {"input": {"arr": [1, 5, 3, 9, 2]}, "expected": 9},
            {"input": {"arr": [-1, -5, -3]}, "expected": -1},
            {"input": {"arr": [42]}, "expected": 42},
            {"input": {"arr": [7, 7, 7]}, "expected": 7},
        ],
        "difficulty": "easy"
    },
    {
        "id": "p2",
        "name": "is_palindrome",
        "description": "Write a function that checks if a given string is a palindrome (reads the same forwards and backwards), ignoring case.",
        "specification": {
            "precondition": "isinstance(s, str)",
            "postcondition": "result == (s.lower() == s.lower()[::-1])",
            "invariants": []
        },
        "test_cases": [
            {"input": {"s": "racecar"}, "expected": True},
            {"input": {"s": "RaceCar"}, "expected": True},
            {"input": {"s": "hello"}, "expected": False},
            {"input": {"s": ""}, "expected": True},
        ],
        "difficulty": "easy"
    },
    {
        "id": "p3",
        "name": "factorial",
        "description": "Write a function that computes the factorial of a non-negative integer n.",
        "specification": {
            "precondition": "isinstance(n, int) and n >= 0",
            "postcondition": "result == (1 if n == 0 else n * factorial(n-1))",
            "invariants": []
        },
        "test_cases": [
            {"input": {"n": 0}, "expected": 1},
            {"input": {"n": 1}, "expected": 1},
            {"input": {"n": 5}, "expected": 120},
            {"input": {"n": 10}, "expected": 3628800},
        ],
        "difficulty": "easy"
    },
    {
        "id": "p4",
        "name": "binary_search",
        "description": "Write a function that performs binary search on a sorted list and returns the index of the target, or -1 if not found.",
        "specification": {
            "precondition": "arr == sorted(arr) and isinstance(target, int)",
            "postcondition": "(result == -1 and target not in arr) or (arr[result] == target)",
            "invariants": ["low <= high implies arr[low] <= target <= arr[high]"]
        },
        "test_cases": [
            {"input": {"arr": [1, 2, 3, 4, 5], "target": 3}, "expected": 2},
            {"input": {"arr": [1, 2, 3, 4, 5], "target": 6}, "expected": -1},
            {"input": {"arr": [], "target": 1}, "expected": -1},
            {"input": {"arr": [1], "target": 1}, "expected": 0},
        ],
        "difficulty": "medium"
    },
    {
        "id": "p5",
        "name": "merge_sorted_lists",
        "description": "Write a function that merges two sorted lists into a single sorted list.",
        "specification": {
            "precondition": "list1 == sorted(list1) and list2 == sorted(list2)",
            "postcondition": "result == sorted(list1 + list2) and len(result) == len(list1) + len(list2)",
            "invariants": []
        },
        "test_cases": [
            {"input": {"list1": [1, 3, 5], "list2": [2, 4, 6]}, "expected": [1, 2, 3, 4, 5, 6]},
            {"input": {"list1": [], "list2": [1, 2, 3]}, "expected": [1, 2, 3]},
            {"input": {"list1": [1], "list2": [2]}, "expected": [1, 2]},
            {"input": {"list1": [1, 2], "list2": [1, 2]}, "expected": [1, 1, 2, 2]},
        ],
        "difficulty": "medium"
    },
    {
        "id": "p6",
        "name": "gcd",
        "description": "Write a function that computes the greatest common divisor of two positive integers using the Euclidean algorithm.",
        "specification": {
            "precondition": "isinstance(a, int) and isinstance(b, int) and a > 0 and b > 0",
            "postcondition": "a % result == 0 and b % result == 0 and all(a % d != 0 or b % d != 0 for d in range(result + 1, min(a, b) + 1))",
            "invariants": []
        },
        "test_cases": [
            {"input": {"a": 12, "b": 18}, "expected": 6},
            {"input": {"a": 17, "b": 13}, "expected": 1},
            {"input": {"a": 100, "b": 25}, "expected": 25},
            {"input": {"a": 7, "b": 7}, "expected": 7},
        ],
        "difficulty": "medium"
    },
    {
        "id": "p7",
        "name": "is_prime",
        "description": "Write a function that checks if a positive integer greater than 1 is prime.",
        "specification": {
            "precondition": "isinstance(n, int) and n > 1",
            "postcondition": "result == all(n % i != 0 for i in range(2, int(n**0.5) + 1))",
            "invariants": []
        },
        "test_cases": [
            {"input": {"n": 2}, "expected": True},
            {"input": {"n": 17}, "expected": True},
            {"input": {"n": 15}, "expected": False},
            {"input": {"n": 97}, "expected": True},
        ],
        "difficulty": "easy"
    },
    {
        "id": "p8",
        "name": "reverse_list",
        "description": "Write a function that reverses a list in-place and returns it.",
        "specification": {
            "precondition": "isinstance(arr, list)",
            "postcondition": "result == list(reversed(original_arr))",
            "invariants": []
        },
        "test_cases": [
            {"input": {"arr": [1, 2, 3, 4, 5]}, "expected": [5, 4, 3, 2, 1]},
            {"input": {"arr": []}, "expected": []},
            {"input": {"arr": [1]}, "expected": [1]},
            {"input": {"arr": [1, 2]}, "expected": [2, 1]},
        ],
        "difficulty": "easy"
    },
    {
        "id": "p9",
        "name": "count_occurrences",
        "description": "Write a function that counts the number of occurrences of a target value in a list.",
        "specification": {
            "precondition": "isinstance(arr, list)",
            "postcondition": "result == sum(1 for x in arr if x == target)",
            "invariants": []
        },
        "test_cases": [
            {"input": {"arr": [1, 2, 3, 2, 2], "target": 2}, "expected": 3},
            {"input": {"arr": [1, 2, 3], "target": 4}, "expected": 0},
            {"input": {"arr": [], "target": 1}, "expected": 0},
            {"input": {"arr": [5, 5, 5, 5], "target": 5}, "expected": 4},
        ],
        "difficulty": "easy"
    },
    {
        "id": "p10",
        "name": "find_duplicates",
        "description": "Write a function that returns a list of all duplicate elements in the input list (elements that appear more than once).",
        "specification": {
            "precondition": "isinstance(arr, list)",
            "postcondition": "all(arr.count(x) > 1 for x in result) and set(result) == {x for x in arr if arr.count(x) > 1}",
            "invariants": []
        },
        "test_cases": [
            {"input": {"arr": [1, 2, 3, 2, 4, 3]}, "expected": [2, 3]},
            {"input": {"arr": [1, 2, 3]}, "expected": []},
            {"input": {"arr": [1, 1, 1, 1]}, "expected": [1]},
            {"input": {"arr": []}, "expected": []},
        ],
        "difficulty": "medium"
    },
    {
        "id": "p11",
        "name": "sum_of_squares",
        "description": "Write a function that computes the sum of squares of all integers from 1 to n.",
        "specification": {
            "precondition": "isinstance(n, int) and n >= 1",
            "postcondition": "result == sum(i**2 for i in range(1, n+1))",
            "invariants": []
        },
        "test_cases": [
            {"input": {"n": 1}, "expected": 1},
            {"input": {"n": 3}, "expected": 14},
            {"input": {"n": 5}, "expected": 55},
            {"input": {"n": 10}, "expected": 385},
        ],
        "difficulty": "easy"
    },
    {
        "id": "p12",
        "name": "nth_fibonacci",
        "description": "Write a function that returns the nth Fibonacci number (0-indexed, where fib(0)=0, fib(1)=1).",
        "specification": {
            "precondition": "isinstance(n, int) and n >= 0",
            "postcondition": "(n == 0 and result == 0) or (n == 1 and result == 1) or (result == fib(n-1) + fib(n-2))",
            "invariants": []
        },
        "test_cases": [
            {"input": {"n": 0}, "expected": 0},
            {"input": {"n": 1}, "expected": 1},
            {"input": {"n": 10}, "expected": 55},
            {"input": {"n": 15}, "expected": 610},
        ],
        "difficulty": "easy"
    },
    {
        "id": "p13",
        "name": "power",
        "description": "Write a function that computes base raised to the power of exponent (both non-negative integers).",
        "specification": {
            "precondition": "isinstance(base, int) and isinstance(exp, int) and exp >= 0",
            "postcondition": "result == base ** exp",
            "invariants": []
        },
        "test_cases": [
            {"input": {"base": 2, "exp": 10}, "expected": 1024},
            {"input": {"base": 5, "exp": 0}, "expected": 1},
            {"input": {"base": 3, "exp": 4}, "expected": 81},
            {"input": {"base": 1, "exp": 100}, "expected": 1},
        ],
        "difficulty": "easy"
    },
    {
        "id": "p14",
        "name": "rotate_list",
        "description": "Write a function that rotates a list k positions to the right.",
        "specification": {
            "precondition": "isinstance(arr, list) and isinstance(k, int) and k >= 0",
            "postcondition": "len(arr) == 0 or result == arr[-(k % len(arr)):] + arr[:-(k % len(arr))]",
            "invariants": []
        },
        "test_cases": [
            {"input": {"arr": [1, 2, 3, 4, 5], "k": 2}, "expected": [4, 5, 1, 2, 3]},
            {"input": {"arr": [1, 2, 3], "k": 3}, "expected": [1, 2, 3]},
            {"input": {"arr": [], "k": 5}, "expected": []},
            {"input": {"arr": [1], "k": 10}, "expected": [1]},
        ],
        "difficulty": "medium"
    },
    {
        "id": "p15",
        "name": "flatten_list",
        "description": "Write a function that flattens a nested list (list of lists) into a single flat list.",
        "specification": {
            "precondition": "isinstance(nested, list) and all(isinstance(x, list) for x in nested)",
            "postcondition": "result == [item for sublist in nested for item in sublist]",
            "invariants": []
        },
        "test_cases": [
            {"input": {"nested": [[1, 2], [3, 4], [5]]}, "expected": [1, 2, 3, 4, 5]},
            {"input": {"nested": [[], [1], [2, 3]]}, "expected": [1, 2, 3]},
            {"input": {"nested": []}, "expected": []},
            {"input": {"nested": [[1, 2, 3]]}, "expected": [1, 2, 3]},
        ],
        "difficulty": "easy"
    },
    {
        "id": "p16",
        "name": "remove_duplicates",
        "description": "Write a function that removes duplicates from a list while preserving order of first occurrences.",
        "specification": {
            "precondition": "isinstance(arr, list)",
            "postcondition": "all(result.count(x) == 1 for x in result) and result == list(dict.fromkeys(arr))",
            "invariants": []
        },
        "test_cases": [
            {"input": {"arr": [1, 2, 2, 3, 4, 3, 5]}, "expected": [1, 2, 3, 4, 5]},
            {"input": {"arr": [1, 1, 1, 1]}, "expected": [1]},
            {"input": {"arr": []}, "expected": []},
            {"input": {"arr": [1, 2, 3]}, "expected": [1, 2, 3]},
        ],
        "difficulty": "medium"
    },
    {
        "id": "p17",
        "name": "intersection",
        "description": "Write a function that returns the intersection of two lists (common elements).",
        "specification": {
            "precondition": "isinstance(list1, list) and isinstance(list2, list)",
            "postcondition": "set(result) == set(list1) & set(list2)",
            "invariants": []
        },
        "test_cases": [
            {"input": {"list1": [1, 2, 3, 4], "list2": [3, 4, 5, 6]}, "expected": [3, 4]},
            {"input": {"list1": [1, 2], "list2": [3, 4]}, "expected": []},
            {"input": {"list1": [], "list2": [1, 2, 3]}, "expected": []},
            {"input": {"list1": [1, 2, 3], "list2": [1, 2, 3]}, "expected": [1, 2, 3]},
        ],
        "difficulty": "easy"
    },
    {
        "id": "p18",
        "name": "second_largest",
        "description": "Write a function that finds the second largest element in a list of at least 2 distinct integers.",
        "specification": {
            "precondition": "isinstance(arr, list) and len(set(arr)) >= 2",
            "postcondition": "result == sorted(set(arr))[-2]",
            "invariants": []
        },
        "test_cases": [
            {"input": {"arr": [1, 5, 3, 9, 2]}, "expected": 5},
            {"input": {"arr": [10, 10, 9, 8]}, "expected": 9},
            {"input": {"arr": [1, 2]}, "expected": 1},
            {"input": {"arr": [7, 7, 7, 8]}, "expected": 7},
        ],
        "difficulty": "medium"
    },
    {
        "id": "p19",
        "name": "string_compression",
        "description": "Write a function that compresses a string by counting consecutive repeated characters (e.g., 'aabccc' -> 'a2b1c3').",
        "specification": {
            "precondition": "isinstance(s, str)",
            "postcondition": "decompressed(result) == s",
            "invariants": []
        },
        "test_cases": [
            {"input": {"s": "aabccc"}, "expected": "a2b1c3"},
            {"input": {"s": "aaaa"}, "expected": "a4"},
            {"input": {"s": "abc"}, "expected": "a1b1c1"},
            {"input": {"s": ""}, "expected": ""},
        ],
        "difficulty": "medium"
    },
    {
        "id": "p20",
        "name": "valid_parentheses",
        "description": "Write a function that checks if a string of parentheses (containing only '(' and ')') is valid (properly nested and matched).",
        "specification": {
            "precondition": "isinstance(s, str) and all(c in '()' for c in s)",
            "postcondition": "result == (s.count('(') == s.count(')') and valid_nesting(s))",
            "invariants": ["count >= 0"]
        },
        "test_cases": [
            {"input": {"s": "(())"}, "expected": True},
            {"input": {"s": "(()"}, "expected": False},
            {"input": {"s": "()()"}, "expected": True},
            {"input": {"s": ")("}, "expected": False},
        ],
        "difficulty": "medium"
    },
    {
        "id": "p21",
        "name": "two_sum",
        "description": "Write a function that finds two numbers in a list that add up to a target sum and returns their indices.",
        "specification": {
            "precondition": "isinstance(nums, list) and isinstance(target, int)",
            "postcondition": "(result is None and no two nums sum to target) or (nums[result[0]] + nums[result[1]] == target)",
            "invariants": []
        },
        "test_cases": [
            {"input": {"nums": [2, 7, 11, 15], "target": 9}, "expected": [0, 1]},
            {"input": {"nums": [3, 2, 4], "target": 6}, "expected": [1, 2]},
            {"input": {"nums": [1, 2, 3], "target": 10}, "expected": None},
            {"input": {"nums": [3, 3], "target": 6}, "expected": [0, 1]},
        ],
        "difficulty": "medium"
    },
    {
        "id": "p22",
        "name": "longest_consecutive",
        "description": "Write a function that finds the length of the longest consecutive sequence in an unsorted list.",
        "specification": {
            "precondition": "isinstance(nums, list)",
            "postcondition": "result == max_consecutive_length(nums)",
            "invariants": []
        },
        "test_cases": [
            {"input": {"nums": [100, 4, 200, 1, 3, 2]}, "expected": 4},
            {"input": {"nums": [0, 3, 7, 2, 5, 8, 4, 6, 0, 1]}, "expected": 9},
            {"input": {"nums": []}, "expected": 0},
            {"input": {"nums": [1]}, "expected": 1},
        ],
        "difficulty": "hard"
    },
    {
        "id": "p23",
        "name": "matrix_transpose",
        "description": "Write a function that transposes a 2D matrix (swaps rows and columns).",
        "specification": {
            "precondition": "isinstance(matrix, list) and all(isinstance(row, list) for row in matrix)",
            "postcondition": "result[j][i] == matrix[i][j] for all valid i, j",
            "invariants": []
        },
        "test_cases": [
            {"input": {"matrix": [[1, 2, 3], [4, 5, 6]]}, "expected": [[1, 4], [2, 5], [3, 6]]},
            {"input": {"matrix": [[1]]}, "expected": [[1]]},
            {"input": {"matrix": []}, "expected": []},
            {"input": {"matrix": [[1, 2], [3, 4]]}, "expected": [[1, 3], [2, 4]]},
        ],
        "difficulty": "medium"
    },
    {
        "id": "p24",
        "name": "anagram_check",
        "description": "Write a function that checks if two strings are anagrams of each other (same characters, different order).",
        "specification": {
            "precondition": "isinstance(s1, str) and isinstance(s2, str)",
            "postcondition": "result == (sorted(s1.lower()) == sorted(s2.lower()))",
            "invariants": []
        },
        "test_cases": [
            {"input": {"s1": "listen", "s2": "silent"}, "expected": True},
            {"input": {"s1": "hello", "s2": "world"}, "expected": False},
            {"input": {"s1": "Anagram", "s2": "Nagaram"}, "expected": True},
            {"input": {"s1": "", "s2": ""}, "expected": True},
        ],
        "difficulty": "easy"
    },
    {
        "id": "p25",
        "name": "kadanes_algorithm",
        "description": "Write a function that finds the maximum sum of a contiguous subarray (Kadane's algorithm).",
        "specification": {
            "precondition": "isinstance(nums, list) and len(nums) > 0",
            "postcondition": "result == max(sum(nums[i:j]) for i in range(len(nums)) for j in range(i+1, len(nums)+1))",
            "invariants": []
        },
        "test_cases": [
            {"input": {"nums": [-2, 1, -3, 4, -1, 2, 1, -5, 4]}, "expected": 6},
            {"input": {"nums": [1]}, "expected": 1},
            {"input": {"nums": [5, 4, -1, 7, 8]}, "expected": 23},
            {"input": {"nums": [-1, -2, -3]}, "expected": -1},
        ],
        "difficulty": "medium"
    },
    {
        "id": "p26",
        "name": "lcm",
        "description": "Write a function that computes the least common multiple of two positive integers.",
        "specification": {
            "precondition": "isinstance(a, int) and isinstance(b, int) and a > 0 and b > 0",
            "postcondition": "result % a == 0 and result % b == 0 and result == (a * b) // gcd(a, b)",
            "invariants": []
        },
        "test_cases": [
            {"input": {"a": 12, "b": 18}, "expected": 36},
            {"input": {"a": 5, "b": 7}, "expected": 35},
            {"input": {"a": 4, "b": 6}, "expected": 12},
            {"input": {"a": 21, "b": 6}, "expected": 42},
        ],
        "difficulty": "medium"
    },
    {
        "id": "p27",
        "name": "is_sorted",
        "description": "Write a function that checks if a list is sorted in non-decreasing order.",
        "specification": {
            "precondition": "isinstance(arr, list)",
            "postcondition": "result == all(arr[i] <= arr[i+1] for i in range(len(arr)-1))",
            "invariants": []
        },
        "test_cases": [
            {"input": {"arr": [1, 2, 3, 4, 5]}, "expected": True},
            {"input": {"arr": [1, 3, 2, 4, 5]}, "expected": False},
            {"input": {"arr": []}, "expected": True},
            {"input": {"arr": [1, 1, 1]}, "expected": True},
        ],
        "difficulty": "easy"
    },
    {
        "id": "p28",
        "name": "running_sum",
        "description": "Write a function that returns the running sum of a list (cumulative sum at each position).",
        "specification": {
            "precondition": "isinstance(nums, list)",
            "postcondition": "result[i] == sum(nums[:i+1]) for all i",
            "invariants": []
        },
        "test_cases": [
            {"input": {"nums": [1, 2, 3, 4]}, "expected": [1, 3, 6, 10]},
            {"input": {"nums": [1, 1, 1, 1, 1]}, "expected": [1, 2, 3, 4, 5]},
            {"input": {"nums": []}, "expected": []},
            {"input": {"nums": [3, 1, 2, 10, 1]}, "expected": [3, 4, 6, 16, 17]},
        ],
        "difficulty": "easy"
    },
    {
        "id": "p29",
        "name": "partition_list",
        "description": "Write a function that partitions a list into elements less than pivot and elements greater than or equal to pivot.",
        "specification": {
            "precondition": "isinstance(arr, list) and isinstance(pivot, int)",
            "postcondition": "all(x < pivot for x in result[0]) and all(x >= pivot for x in result[1])",
            "invariants": []
        },
        "test_cases": [
            {"input": {"arr": [1, 4, 3, 2, 5], "pivot": 3}, "expected": [[1, 2], [4, 3, 5]]},
            {"input": {"arr": [5, 5, 5], "pivot": 5}, "expected": [[], [5, 5, 5]]},
            {"input": {"arr": [], "pivot": 3}, "expected": [[], []]},
            {"input": {"arr": [1, 2, 3], "pivot": 10}, "expected": [[1, 2, 3], []]},
        ],
        "difficulty": "medium"
    },
    {
        "id": "p30",
        "name": "count_words",
        "description": "Write a function that counts the number of words in a string (words are separated by spaces).",
        "specification": {
            "precondition": "isinstance(s, str)",
            "postcondition": "result == len(s.split())",
            "invariants": []
        },
        "test_cases": [
            {"input": {"s": "hello world"}, "expected": 2},
            {"input": {"s": "  one   two  three  "}, "expected": 3},
            {"input": {"s": ""}, "expected": 0},
            {"input": {"s": "word"}, "expected": 1},
        ],
        "difficulty": "easy"
    }
]

def get_benchmark_problems(num_samples=None):
    """Get benchmark problems for evaluation."""
    if num_samples is None:
        return BENCHMARK_PROBLEMS
    return BENCHMARK_PROBLEMS[:min(num_samples, len(BENCHMARK_PROBLEMS))]
