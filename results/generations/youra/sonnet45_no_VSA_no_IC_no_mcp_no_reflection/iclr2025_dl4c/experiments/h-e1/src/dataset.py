"""Minimal CodeContests dataset loader for fix-impact-ratio validation."""

import json
from dataclasses import dataclass, asdict
from typing import List
from pathlib import Path

@dataclass
class TestCase:
    input: str
    expected_output: str

@dataclass
class Problem:
    problem_id: str
    statement: str
    solution: str
    test_cases: List[TestCase]

    def to_dict(self):
        return {
            **asdict(self),
            'test_cases': [asdict(tc) for tc in self.test_cases]
        }

    @classmethod
    def from_dict(cls, d):
        test_cases = [TestCase(**tc) for tc in d['test_cases']]
        return cls(
            problem_id=d['problem_id'],
            statement=d['statement'],
            solution=d['solution'],
            test_cases=test_cases
        )

def create_synthetic_problems() -> List[Problem]:
    """Create 10 synthetic problems with 15+ test cases each."""

    problems = [
        # Problem 1: Sum of two numbers (edge cases: negative, zero, large)
        Problem(
            problem_id="p001",
            statement="Read two integers a and b. Print their sum.",
            solution="a, b = map(int, input().split())\nprint(a + b)",
            test_cases=[
                TestCase("1 2", "3"),
                TestCase("0 0", "0"),
                TestCase("-1 1", "0"),
                TestCase("100 200", "300"),
                TestCase("-50 -50", "-100"),
                TestCase("999999 1", "1000000"),
                TestCase("-1000000 1000000", "0"),
                TestCase("42 0", "42"),
                TestCase("0 42", "42"),
                TestCase("-1 -1", "-2"),
                TestCase("7 8", "15"),
                TestCase("123 456", "579"),
                TestCase("-999 999", "0"),
                TestCase("1 1", "2"),
                TestCase("2 3", "5"),
            ]
        ),

        # Problem 2: Max of three numbers
        Problem(
            problem_id="p002",
            statement="Read three integers. Print the maximum.",
            solution="a, b, c = map(int, input().split())\nprint(max(a, b, c))",
            test_cases=[
                TestCase("1 2 3", "3"),
                TestCase("3 2 1", "3"),
                TestCase("2 3 1", "3"),
                TestCase("5 5 5", "5"),
                TestCase("-1 -2 -3", "-1"),
                TestCase("0 0 0", "0"),
                TestCase("100 50 75", "100"),
                TestCase("-10 0 10", "10"),
                TestCase("7 7 6", "7"),
                TestCase("999 998 997", "999"),
                TestCase("-100 -200 -150", "-100"),
                TestCase("42 41 40", "42"),
                TestCase("1 1 2", "2"),
                TestCase("2 1 1", "2"),
                TestCase("1 2 1", "2"),
            ]
        ),

        # Problem 3: Array sum
        Problem(
            problem_id="p003",
            statement="Read n, then n integers. Print their sum.",
            solution="n = int(input())\narr = list(map(int, input().split()))\nprint(sum(arr))",
            test_cases=[
                TestCase("3\n1 2 3", "6"),
                TestCase("1\n42", "42"),
                TestCase("5\n1 1 1 1 1", "5"),
                TestCase("4\n-1 -2 -3 -4", "-10"),
                TestCase("2\n0 0", "0"),
                TestCase("3\n100 200 300", "600"),
                TestCase("4\n-5 5 -10 10", "0"),
                TestCase("6\n1 2 3 4 5 6", "21"),
                TestCase("3\n999 1 0", "1000"),
                TestCase("2\n-1000 1000", "0"),
                TestCase("5\n10 20 30 40 50", "150"),
                TestCase("4\n7 8 9 10", "34"),
                TestCase("3\n-1 0 1", "0"),
                TestCase("2\n50 50", "100"),
                TestCase("1\n0", "0"),
            ]
        ),

        # Problem 4: Even/Odd count
        Problem(
            problem_id="p004",
            statement="Read n, then n integers. Print count of even numbers.",
            solution="n = int(input())\narr = list(map(int, input().split()))\nprint(sum(1 for x in arr if x % 2 == 0))",
            test_cases=[
                TestCase("3\n1 2 3", "1"),
                TestCase("4\n2 4 6 8", "4"),
                TestCase("5\n1 3 5 7 9", "0"),
                TestCase("2\n0 0", "2"),
                TestCase("4\n-2 -4 1 3", "2"),
                TestCase("3\n10 11 12", "2"),
                TestCase("6\n1 2 3 4 5 6", "3"),
                TestCase("1\n42", "1"),
                TestCase("1\n7", "0"),
                TestCase("5\n0 1 2 3 4", "3"),
                TestCase("4\n-1 -2 -3 -4", "2"),
                TestCase("3\n100 101 102", "2"),
                TestCase("2\n13 14", "1"),
                TestCase("3\n20 21 22", "2"),
                TestCase("4\n5 10 15 20", "2"),
            ]
        ),

        # Problem 5: String reverse
        Problem(
            problem_id="p005",
            statement="Read a string. Print it reversed.",
            solution="s = input()\nprint(s[::-1])",
            test_cases=[
                TestCase("hello", "olleh"),
                TestCase("a", "a"),
                TestCase("ab", "ba"),
                TestCase("abc", "cba"),
                TestCase("12345", "54321"),
                TestCase("racecar", "racecar"),
                TestCase("python", "nohtyp"),
                TestCase("test", "tset"),
                TestCase("xyz", "zyx"),
                TestCase("world", "dlrow"),
                TestCase("code", "edoc"),
                TestCase("reverse", "esrever"),
                TestCase("data", "atad"),
                TestCase("1234567890", "0987654321"),
                TestCase("ab cd ef", "fe dc ba"),
            ]
        ),

        # Problem 6: Palindrome check
        Problem(
            problem_id="p006",
            statement="Read a string. Print YES if palindrome, else NO.",
            solution="s = input()\nprint('YES' if s == s[::-1] else 'NO')",
            test_cases=[
                TestCase("aba", "YES"),
                TestCase("abc", "NO"),
                TestCase("a", "YES"),
                TestCase("aa", "YES"),
                TestCase("ab", "NO"),
                TestCase("racecar", "YES"),
                TestCase("hello", "NO"),
                TestCase("noon", "YES"),
                TestCase("world", "NO"),
                TestCase("level", "YES"),
                TestCase("python", "NO"),
                TestCase("madam", "YES"),
                TestCase("test", "NO"),
                TestCase("radar", "YES"),
                TestCase("code", "NO"),
            ]
        ),

        # Problem 7: Factorial
        Problem(
            problem_id="p007",
            statement="Read n. Print n! (factorial).",
            solution="n = int(input())\nresult = 1\nfor i in range(1, n+1):\n    result *= i\nprint(result)",
            test_cases=[
                TestCase("0", "1"),
                TestCase("1", "1"),
                TestCase("2", "2"),
                TestCase("3", "6"),
                TestCase("4", "24"),
                TestCase("5", "120"),
                TestCase("6", "720"),
                TestCase("7", "5040"),
                TestCase("8", "40320"),
                TestCase("9", "362880"),
                TestCase("10", "3628800"),
                TestCase("11", "39916800"),
                TestCase("12", "479001600"),
                TestCase("13", "6227020800"),
                TestCase("14", "87178291200"),
            ]
        ),

        # Problem 8: GCD
        Problem(
            problem_id="p008",
            statement="Read two integers a and b. Print their GCD.",
            solution="import math\na, b = map(int, input().split())\nprint(math.gcd(a, b))",
            test_cases=[
                TestCase("12 8", "4"),
                TestCase("1 1", "1"),
                TestCase("10 5", "5"),
                TestCase("7 3", "1"),
                TestCase("100 50", "50"),
                TestCase("18 24", "6"),
                TestCase("15 25", "5"),
                TestCase("21 14", "7"),
                TestCase("9 6", "3"),
                TestCase("30 45", "15"),
                TestCase("8 12", "4"),
                TestCase("20 30", "10"),
                TestCase("13 17", "1"),
                TestCase("36 48", "12"),
                TestCase("50 75", "25"),
            ]
        ),

        # Problem 9: Prime check
        Problem(
            problem_id="p009",
            statement="Read n. Print YES if prime, else NO.",
            solution="n = int(input())\nif n < 2:\n    print('NO')\nelse:\n    is_prime = True\n    for i in range(2, int(n**0.5)+1):\n        if n % i == 0:\n            is_prime = False\n            break\n    print('YES' if is_prime else 'NO')",
            test_cases=[
                TestCase("2", "YES"),
                TestCase("3", "YES"),
                TestCase("4", "NO"),
                TestCase("5", "YES"),
                TestCase("6", "NO"),
                TestCase("7", "YES"),
                TestCase("8", "NO"),
                TestCase("9", "NO"),
                TestCase("10", "NO"),
                TestCase("11", "YES"),
                TestCase("1", "NO"),
                TestCase("13", "YES"),
                TestCase("17", "YES"),
                TestCase("20", "NO"),
                TestCase("23", "YES"),
            ]
        ),

        # Problem 10: Fibonacci
        Problem(
            problem_id="p010",
            statement="Read n. Print the n-th Fibonacci number (0-indexed).",
            solution="n = int(input())\nif n == 0:\n    print(0)\nelif n == 1:\n    print(1)\nelse:\n    a, b = 0, 1\n    for _ in range(2, n+1):\n        a, b = b, a+b\n    print(b)",
            test_cases=[
                TestCase("0", "0"),
                TestCase("1", "1"),
                TestCase("2", "1"),
                TestCase("3", "2"),
                TestCase("4", "3"),
                TestCase("5", "5"),
                TestCase("6", "8"),
                TestCase("7", "13"),
                TestCase("8", "21"),
                TestCase("9", "34"),
                TestCase("10", "55"),
                TestCase("11", "89"),
                TestCase("12", "144"),
                TestCase("13", "233"),
                TestCase("14", "377"),
            ]
        ),
    ]

    return problems

def save_dataset(problems: List[Problem], path: Path):
    """Save problems to JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [p.to_dict() for p in problems]
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def load_dataset(path: Path) -> List[Problem]:
    """Load problems from JSON."""
    with open(path) as f:
        data = json.load(f)
    return [Problem.from_dict(d) for d in data]

if __name__ == "__main__":
    problems = create_synthetic_problems()
    save_dataset(problems, Path("experiments/h-e1/data/problems.json"))
    print(f"Created {len(problems)} problems with {sum(len(p.test_cases) for p in problems)} total test cases")
