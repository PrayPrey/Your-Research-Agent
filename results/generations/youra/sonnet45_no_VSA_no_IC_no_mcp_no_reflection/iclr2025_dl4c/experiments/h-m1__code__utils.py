"""Data structures for h-m1 experiment."""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class ErrorType(Enum):
    SYNTAX = "syntax"
    RUNTIME = "runtime"
    LOGIC = "logic"
    EDGE_CASE = "edge_case"


@dataclass
class TestCase:
    case_id: int
    input_data: str
    expected_output: str


@dataclass
class Problem:
    problem_id: str
    title: str
    rating: int
    solve_count: int
    test_cases: List[TestCase]


@dataclass
class TestFailure:
    test_id: int
    iteration: int
    error_msg: str
    input_data: str
    expected: str
    actual: str
    error_type: Optional[ErrorType] = None


@dataclass
class DebugIteration:
    iteration: int
    code: str
    passing_count: int
    failing_test_ids: List[int]


@dataclass
class DebugSession:
    problem_id: str
    iterations: List[DebugIteration]
    fix_sequence: List[int]  # Test IDs in fix order
    failures: List[TestFailure]
