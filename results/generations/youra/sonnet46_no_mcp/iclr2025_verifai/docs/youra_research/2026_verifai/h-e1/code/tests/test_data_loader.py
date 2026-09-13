import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from data_loader import load_humaneval_plus, load_mbpp_plus, validate_datasets


def test_humaneval_size():
    he = load_humaneval_plus()
    assert len(he) == 164, f"Expected 164 problems, got {len(he)}"


def test_mbpp_size():
    mbpp = load_mbpp_plus()
    assert len(mbpp) in (374, 378), f"Expected 374 or 378 problems, got {len(mbpp)}"


def test_problem_keys():
    he = load_humaneval_plus()
    first = next(iter(he.values()))
    assert "task_id" in first or "prompt" in first, "Missing expected keys"


def test_validate_passes():
    he = load_humaneval_plus()
    mbpp = load_mbpp_plus()
    assert validate_datasets(he, mbpp) is True


def test_validate_wrong_size():
    he = load_humaneval_plus()
    mbpp = load_mbpp_plus()
    with pytest.raises(ValueError):
        validate_datasets({}, mbpp)
