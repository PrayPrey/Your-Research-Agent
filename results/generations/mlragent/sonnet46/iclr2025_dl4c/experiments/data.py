"""
Problem dataset for HierAlign experiment.
Uses a subset of HumanEval-style problems with test cases.
"""

PROBLEMS = [
    {
        "task_id": "HE_1",
        "prompt": "Write a Python function `has_close_elements(numbers, threshold)` that checks if any two numbers in a list are closer than a given threshold.\n\n>>> has_close_elements([1.0, 2.0, 3.0], 0.5)\nFalse\n>>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)\nTrue",
        "entry_point": "has_close_elements",
        "tests": [
            "assert has_close_elements([1.0, 2.0, 3.0], 0.5) == False",
            "assert has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3) == True",
            "assert has_close_elements([1.0, 2.0, 3.0], 0.1) == False",
            "assert has_close_elements([1.0, 1.01, 3.0], 0.02) == True",
            "assert has_close_elements([], 0.5) == False",
        ]
    },
    {
        "task_id": "HE_2",
        "prompt": "Write a Python function `separate_paren_groups(paren_string)` that takes a string of multiple nested parenthesis groups and separates them into separate strings. Each group is balanced and not nested within another group.\n\n>>> separate_paren_groups('( ) (( )) (( )( ))')\n['()', '(())', '(()())']",
        "entry_point": "separate_paren_groups",
        "tests": [
            "assert separate_paren_groups('( ) (( )) (( )( ))') == ['()', '(())', '(()())']",
            "assert separate_paren_groups('( ) (( ))') == ['()', '(())']",
            "assert separate_paren_groups('(())') == ['(())']",
        ]
    },
    {
        "task_id": "HE_3",
        "prompt": "Write a Python function `truncate_number(number)` that takes a positive floating point number and returns the decimal part of it.\n\n>>> truncate_number(3.5)\n0.5",
        "entry_point": "truncate_number",
        "tests": [
            "assert truncate_number(3.5) == 0.5",
            "assert truncate_number(1.25) == 0.25",
            "assert abs(truncate_number(123.0) - 0.0) < 1e-6",
            "assert abs(truncate_number(0.1) - 0.1) < 1e-6",
        ]
    },
    {
        "task_id": "HE_4",
        "prompt": "Write a Python function `below_zero(operations)` that takes a list of deposit and withdrawal operations on a bank account starting with a zero balance. Return True if at any point the balance falls below zero, otherwise return False.\n\n>>> below_zero([1, 2, 3])\nFalse\n>>> below_zero([1, 2, -4, 5])\nTrue",
        "entry_point": "below_zero",
        "tests": [
            "assert below_zero([1, 2, 3]) == False",
            "assert below_zero([1, 2, -4, 5]) == True",
            "assert below_zero([]) == False",
            "assert below_zero([3, -2, -1]) == False",
            "assert below_zero([3, -2, -2]) == True",
        ]
    },
    {
        "task_id": "HE_5",
        "prompt": "Write a Python function `mean_absolute_deviation(numbers)` that calculates the Mean Absolute Deviation around the mean of a dataset.\n\n>>> mean_absolute_deviation([1.0, 2.0, 3.0, 4.0])\n1.0",
        "entry_point": "mean_absolute_deviation",
        "tests": [
            "assert abs(mean_absolute_deviation([1.0, 2.0, 3.0, 4.0]) - 1.0) < 1e-6",
            "assert abs(mean_absolute_deviation([1.0, 1.0, 1.0]) - 0.0) < 1e-6",
            "assert abs(mean_absolute_deviation([1.0, 2.0]) - 0.5) < 1e-6",
        ]
    },
    {
        "task_id": "HE_6",
        "prompt": "Write a Python function `intersperse(numbers, delimiter)` that inserts a number 'delimiter' between every two consecutive elements of the input list.\n\n>>> intersperse([], 4)\n[]\n>>> intersperse([1, 2, 3], 4)\n[1, 4, 2, 4, 3]",
        "entry_point": "intersperse",
        "tests": [
            "assert intersperse([], 4) == []",
            "assert intersperse([1, 2, 3], 4) == [1, 4, 2, 4, 3]",
            "assert intersperse([1], 4) == [1]",
            "assert intersperse([1, 2], 9) == [1, 9, 2]",
        ]
    },
    {
        "task_id": "HE_7",
        "prompt": "Write a Python function `parse_nested_parens(paren_string)` that takes a string representing several groups of nested parentheses separated by spaces. For each group, return the maximum nesting level.\n\n>>> parse_nested_parens('(()()) ((())) () ((()()()))')\n[2, 3, 1, 3]",
        "entry_point": "parse_nested_parens",
        "tests": [
            "assert parse_nested_parens('(()()) ((())) () ((()()()))') == [2, 3, 1, 3]",
            "assert parse_nested_parens('() (())') == [1, 2]",
            "assert parse_nested_parens('((()())))') == [4]",
        ]
    },
    {
        "task_id": "HE_8",
        "prompt": "Write a Python function `filter_by_substring(strings, substring)` that filters a list of strings to return only those that contain the given substring.\n\n>>> filter_by_substring([], 'a')\n[]\n>>> filter_by_substring(['abc', 'bacd', 'cde', 'array'], 'a')\n['abc', 'bacd', 'array']",
        "entry_point": "filter_by_substring",
        "tests": [
            "assert filter_by_substring([], 'a') == []",
            "assert filter_by_substring(['abc', 'bacd', 'cde', 'array'], 'a') == ['abc', 'bacd', 'array']",
            "assert filter_by_substring(['xxx', 'yyy'], 'z') == []",
            "assert filter_by_substring(['hello', 'world', 'help'], 'hel') == ['hello', 'help']",
        ]
    },
    {
        "task_id": "HE_9",
        "prompt": "Write a Python function `sum_product(numbers)` that returns a tuple containing the sum and the product of all integers in a list.\n\n>>> sum_product([])\n(0, 1)\n>>> sum_product([1, 2, 3, 4])\n(10, 24)",
        "entry_point": "sum_product",
        "tests": [
            "assert sum_product([]) == (0, 1)",
            "assert sum_product([1, 2, 3, 4]) == (10, 24)",
            "assert sum_product([1]) == (1, 1)",
            "assert sum_product([0, 1, 2]) == (3, 0)",
        ]
    },
    {
        "task_id": "HE_10",
        "prompt": "Write a Python function `rolling_max(numbers)` that takes a list of integers and returns a list of rolling maximum elements found until a given moment in the sequence.\n\n>>> rolling_max([1, 2, 3, 2, 3, 4, 2])\n[1, 2, 3, 3, 3, 4, 4]",
        "entry_point": "rolling_max",
        "tests": [
            "assert rolling_max([1, 2, 3, 2, 3, 4, 2]) == [1, 2, 3, 3, 3, 4, 4]",
            "assert rolling_max([3, 2, 1]) == [3, 3, 3]",
            "assert rolling_max([1]) == [1]",
            "assert rolling_max([]) == []",
        ]
    },
    {
        "task_id": "HE_11",
        "prompt": "Write a Python function `is_palindrome(string)` that checks if a given string is a palindrome.\n\n>>> is_palindrome('')\nTrue\n>>> is_palindrome('aba')\nTrue\n>>> is_palindrome('hello')\nFalse",
        "entry_point": "is_palindrome",
        "tests": [
            "assert is_palindrome('') == True",
            "assert is_palindrome('aba') == True",
            "assert is_palindrome('hello') == False",
            "assert is_palindrome('racecar') == True",
            "assert is_palindrome('abba') == True",
        ]
    },
    {
        "task_id": "HE_12",
        "prompt": "Write a Python function `string_xor(a, b)` that takes two binary strings (consisting of '0's and '1's) of the same length and returns their XOR.\n\n>>> string_xor('010', '110')\n'100'",
        "entry_point": "string_xor",
        "tests": [
            "assert string_xor('010', '110') == '100'",
            "assert string_xor('111', '000') == '111'",
            "assert string_xor('010', '010') == '000'",
            "assert string_xor('1', '0') == '1'",
        ]
    },
    {
        "task_id": "HE_13",
        "prompt": "Write a Python function `longest(strings)` that returns the longest string from a list, or None if the list is empty.\n\n>>> longest([])\n>>> longest(['a', 'bb', 'ccc'])\n'ccc'",
        "entry_point": "longest",
        "tests": [
            "assert longest([]) is None",
            "assert longest(['a', 'bb', 'ccc']) == 'ccc'",
            "assert longest(['a', 'b', 'c']) == 'a'",
            "assert longest(['hello', 'world']) == 'hello'",
        ]
    },
    {
        "task_id": "HE_14",
        "prompt": "Write a Python function `greatest_common_divisor(a, b)` that computes the GCD of two integers.\n\n>>> greatest_common_divisor(3, 5)\n1\n>>> greatest_common_divisor(25, 15)\n5",
        "entry_point": "greatest_common_divisor",
        "tests": [
            "assert greatest_common_divisor(3, 5) == 1",
            "assert greatest_common_divisor(25, 15) == 5",
            "assert greatest_common_divisor(12, 8) == 4",
            "assert greatest_common_divisor(7, 7) == 7",
        ]
    },
    {
        "task_id": "HE_15",
        "prompt": "Write a Python function `all_prefixes(string)` that returns a list of all prefixes of a given string from shortest to longest.\n\n>>> all_prefixes('abc')\n['a', 'ab', 'abc']",
        "entry_point": "all_prefixes",
        "tests": [
            "assert all_prefixes('abc') == ['a', 'ab', 'abc']",
            "assert all_prefixes('') == []",
            "assert all_prefixes('x') == ['x']",
            "assert all_prefixes('abcd') == ['a', 'ab', 'abc', 'abcd']",
        ]
    },
    {
        "task_id": "HE_16",
        "prompt": "Write a Python function `count_distinct_characters(string)` that returns the number of distinct characters in a string (case-insensitive).\n\n>>> count_distinct_characters('Hello World')\n8",
        "entry_point": "count_distinct_characters",
        "tests": [
            "assert count_distinct_characters('Hello World') == 8",
            "assert count_distinct_characters('') == 0",
            "assert count_distinct_characters('aAbB') == 2",
            "assert count_distinct_characters('abcd') == 4",
        ]
    },
    {
        "task_id": "HE_17",
        "prompt": "Write a Python function `sort_numbers(numbers)` that takes a space-delimited string of number names ('zero' through 'nine') and returns them sorted from smallest to largest.\n\n>>> sort_numbers('three one five')\n'one three five'",
        "entry_point": "sort_numbers",
        "tests": [
            "assert sort_numbers('three one five') == 'one three five'",
            "assert sort_numbers('') == ''",
            "assert sort_numbers('zero') == 'zero'",
            "assert sort_numbers('nine eight seven') == 'seven eight nine'",
        ]
    },
    {
        "task_id": "HE_18",
        "prompt": "Write a Python function `find_closest_elements(numbers)` that takes a list of numbers and finds the two closest values. Return them in sorted order (smaller first).\n\n>>> find_closest_elements([1.0, 2.0, 3.0, 4.0, 5.0, 2.2])\n(2.0, 2.2)",
        "entry_point": "find_closest_elements",
        "tests": [
            "assert find_closest_elements([1.0, 2.0, 3.0, 4.0, 5.0, 2.2]) == (2.0, 2.2)",
            "assert find_closest_elements([1.0, 5.0, 3.0]) == (1.0, 3.0)",
            "assert find_closest_elements([1.0, 2.0]) == (1.0, 2.0)",
        ]
    },
    {
        "task_id": "HE_19",
        "prompt": "Write a Python function `rescale_to_unit(numbers)` that rescales a list of numbers so that the minimum becomes 0 and the maximum becomes 1.\n\n>>> rescale_to_unit([1.0, 2.0, 3.0, 4.0, 5.0])\n[0.0, 0.25, 0.5, 0.75, 1.0]",
        "entry_point": "rescale_to_unit",
        "tests": [
            "assert rescale_to_unit([1.0, 2.0, 3.0, 4.0, 5.0]) == [0.0, 0.25, 0.5, 0.75, 1.0]",
            "assert rescale_to_unit([1.0, 1.0]) == [0.0, 0.0]",
            "assert rescale_to_unit([0.0, 10.0]) == [0.0, 1.0]",
        ]
    },
    {
        "task_id": "HE_20",
        "prompt": "Write a Python function `flip_case(string)` that swaps the case of each character in the string.\n\n>>> flip_case('Hello')\n'hELLO'",
        "entry_point": "flip_case",
        "tests": [
            "assert flip_case('Hello') == 'hELLO'",
            "assert flip_case('') == ''",
            "assert flip_case('abc') == 'ABC'",
            "assert flip_case('ABC') == 'abc'",
            "assert flip_case('a1b2') == 'A1B2'",
        ]
    },
]


def get_problems():
    return PROBLEMS


def get_problem_by_id(task_id):
    for p in PROBLEMS:
        if p["task_id"] == task_id:
            return p
    return None
