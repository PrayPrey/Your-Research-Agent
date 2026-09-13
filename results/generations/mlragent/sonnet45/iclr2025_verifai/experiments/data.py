"""
Dataset and problem generation for Neural-Symbolic Repair experiments
"""
import json
import random
from typing import List, Dict, Tuple

class ProgrammingProblem:
    """Represents a programming problem with specification and test cases"""
    def __init__(self, problem_id: int, name: str, description: str,
                 function_signature: str, test_cases: List[Dict],
                 reference_solution: str = None):
        self.problem_id = problem_id
        self.name = name
        self.description = description
        self.function_signature = function_signature
        self.test_cases = test_cases
        self.reference_solution = reference_solution

    def to_dict(self):
        return {
            "problem_id": self.problem_id,
            "name": self.name,
            "description": self.description,
            "function_signature": self.function_signature,
            "test_cases": self.test_cases,
            "reference_solution": self.reference_solution
        }

def generate_problem_dataset(num_problems: int = 50, seed: int = 42) -> List[ProgrammingProblem]:
    """Generate a dataset of programming problems for testing"""
    random.seed(seed)

    problems = [
        ProgrammingProblem(
            problem_id=1,
            name="Two Sum",
            description="Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target. You may assume that each input would have exactly one solution, and you may not use the same element twice.",
            function_signature="def two_sum(nums: List[int], target: int) -> List[int]:",
            test_cases=[
                {"input": {"nums": [2, 7, 11, 15], "target": 9}, "expected": [0, 1]},
                {"input": {"nums": [3, 2, 4], "target": 6}, "expected": [1, 2]},
                {"input": {"nums": [3, 3], "target": 6}, "expected": [0, 1]},
            ],
            reference_solution="""def two_sum(nums: List[int], target: int) -> List[int]:
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []"""
        ),
        ProgrammingProblem(
            problem_id=2,
            name="Palindrome Number",
            description="Given an integer x, return true if x is a palindrome, and false otherwise. An integer is a palindrome when it reads the same backward as forward.",
            function_signature="def is_palindrome(x: int) -> bool:",
            test_cases=[
                {"input": {"x": 121}, "expected": True},
                {"input": {"x": -121}, "expected": False},
                {"input": {"x": 10}, "expected": False},
                {"input": {"x": 0}, "expected": True},
            ],
            reference_solution="""def is_palindrome(x: int) -> bool:
    if x < 0:
        return False
    return str(x) == str(x)[::-1]"""
        ),
        ProgrammingProblem(
            problem_id=3,
            name="Reverse String",
            description="Write a function that reverses a string. The input string is given as an array of characters. You must do this by modifying the input array in-place with O(1) extra memory.",
            function_signature="def reverse_string(s: List[str]) -> None:",
            test_cases=[
                {"input": {"s": ["h", "e", "l", "l", "o"]}, "expected": ["o", "l", "l", "e", "h"]},
                {"input": {"s": ["H", "a", "n", "n", "a", "h"]}, "expected": ["h", "a", "n", "n", "a", "H"]},
            ],
            reference_solution="""def reverse_string(s: List[str]) -> None:
    left, right = 0, len(s) - 1
    while left < right:
        s[left], s[right] = s[right], s[left]
        left += 1
        right -= 1"""
        ),
        ProgrammingProblem(
            problem_id=4,
            name="Valid Parentheses",
            description="Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid. An input string is valid if: Open brackets must be closed by the same type of brackets. Open brackets must be closed in the correct order.",
            function_signature="def is_valid(s: str) -> bool:",
            test_cases=[
                {"input": {"s": "()"}, "expected": True},
                {"input": {"s": "()[]{}"}, "expected": True},
                {"input": {"s": "(]"}, "expected": False},
                {"input": {"s": "([)]"}, "expected": False},
                {"input": {"s": "{[]}"}, "expected": True},
            ],
            reference_solution="""def is_valid(s: str) -> bool:
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}
    for char in s:
        if char in mapping:
            top_element = stack.pop() if stack else '#'
            if mapping[char] != top_element:
                return False
        else:
            stack.append(char)
    return not stack"""
        ),
        ProgrammingProblem(
            problem_id=5,
            name="Merge Sorted Lists",
            description="You are given the heads of two sorted linked lists list1 and list2. Merge the two lists into one sorted list. The list should be made by splicing together the nodes of the first two lists. Return the head of the merged linked list.",
            function_signature="def merge_two_lists(list1: Optional[ListNode], list2: Optional[ListNode]) -> Optional[ListNode]:",
            test_cases=[
                {"input": {"list1": [1,2,4], "list2": [1,3,4]}, "expected": [1,1,2,3,4,4]},
                {"input": {"list1": [], "list2": []}, "expected": []},
                {"input": {"list1": [], "list2": [0]}, "expected": [0]},
            ],
            reference_solution="""def merge_two_lists(list1: Optional[ListNode], list2: Optional[ListNode]) -> Optional[ListNode]:
    dummy = ListNode(0)
    current = dummy
    while list1 and list2:
        if list1.val < list2.val:
            current.next = list1
            list1 = list1.next
        else:
            current.next = list2
            list2 = list2.next
        current = current.next
    current.next = list1 if list1 else list2
    return dummy.next"""
        ),
        ProgrammingProblem(
            problem_id=6,
            name="Maximum Subarray",
            description="Given an integer array nums, find the contiguous subarray (containing at least one number) which has the largest sum and return its sum.",
            function_signature="def max_subarray(nums: List[int]) -> int:",
            test_cases=[
                {"input": {"nums": [-2,1,-3,4,-1,2,1,-5,4]}, "expected": 6},
                {"input": {"nums": [1]}, "expected": 1},
                {"input": {"nums": [5,4,-1,7,8]}, "expected": 23},
            ],
            reference_solution="""def max_subarray(nums: List[int]) -> int:
    max_sum = current_sum = nums[0]
    for num in nums[1:]:
        current_sum = max(num, current_sum + num)
        max_sum = max(max_sum, current_sum)
    return max_sum"""
        ),
        ProgrammingProblem(
            problem_id=7,
            name="Climbing Stairs",
            description="You are climbing a staircase. It takes n steps to reach the top. Each time you can either climb 1 or 2 steps. In how many distinct ways can you climb to the top?",
            function_signature="def climb_stairs(n: int) -> int:",
            test_cases=[
                {"input": {"n": 2}, "expected": 2},
                {"input": {"n": 3}, "expected": 3},
                {"input": {"n": 4}, "expected": 5},
                {"input": {"n": 5}, "expected": 8},
            ],
            reference_solution="""def climb_stairs(n: int) -> int:
    if n <= 2:
        return n
    prev, curr = 1, 2
    for i in range(3, n + 1):
        prev, curr = curr, prev + curr
    return curr"""
        ),
        ProgrammingProblem(
            problem_id=8,
            name="Binary Search",
            description="Given an array of integers nums which is sorted in ascending order, and an integer target, write a function to search target in nums. If target exists, then return its index. Otherwise, return -1.",
            function_signature="def search(nums: List[int], target: int) -> int:",
            test_cases=[
                {"input": {"nums": [-1,0,3,5,9,12], "target": 9}, "expected": 4},
                {"input": {"nums": [-1,0,3,5,9,12], "target": 2}, "expected": -1},
                {"input": {"nums": [5], "target": 5}, "expected": 0},
            ],
            reference_solution="""def search(nums: List[int], target: int) -> int:
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1"""
        ),
        ProgrammingProblem(
            problem_id=9,
            name="First Bad Version",
            description="You are a product manager and currently leading a team to develop a new product. Unfortunately, the latest version of your product fails the quality check. Since each version is developed based on the previous version, all the versions after a bad version are also bad. Suppose you have n versions [1, 2, ..., n] and you want to find out the first bad one, which causes all the following ones to be bad.",
            function_signature="def first_bad_version(n: int) -> int:",
            test_cases=[
                {"input": {"n": 5, "bad": 4}, "expected": 4},
                {"input": {"n": 1, "bad": 1}, "expected": 1},
            ],
            reference_solution="""def first_bad_version(n: int) -> int:
    left, right = 1, n
    while left < right:
        mid = (left + right) // 2
        if isBadVersion(mid):
            right = mid
        else:
            left = mid + 1
    return left"""
        ),
        ProgrammingProblem(
            problem_id=10,
            name="Contains Duplicate",
            description="Given an integer array nums, return true if any value appears at least twice in the array, and return false if every element is distinct.",
            function_signature="def contains_duplicate(nums: List[int]) -> bool:",
            test_cases=[
                {"input": {"nums": [1,2,3,1]}, "expected": True},
                {"input": {"nums": [1,2,3,4]}, "expected": False},
                {"input": {"nums": [1,1,1,3,3,4,3,2,4,2]}, "expected": True},
            ],
            reference_solution="""def contains_duplicate(nums: List[int]) -> bool:
    return len(nums) != len(set(nums))"""
        ),
    ]

    # Return only the requested number of problems
    return problems[:min(num_problems, len(problems))]

def save_dataset(problems: List[ProgrammingProblem], filename: str):
    """Save dataset to JSON file"""
    with open(filename, 'w') as f:
        json.dump([p.to_dict() for p in problems], f, indent=2)

def load_dataset(filename: str) -> List[ProgrammingProblem]:
    """Load dataset from JSON file"""
    with open(filename, 'r') as f:
        data = json.load(f)
    return [ProgrammingProblem(**p) for p in data]
