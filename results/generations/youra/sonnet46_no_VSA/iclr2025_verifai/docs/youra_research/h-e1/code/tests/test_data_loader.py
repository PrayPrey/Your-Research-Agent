"""Tests for data_loader module."""
import sys
import json
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_loader import load_contracteval, get_tasks_with_cvts, get_z3_tractable_ids


def _make_test_jsonl(tasks):
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False)
    for t in tasks:
        tmp.write(json.dumps(t) + "\n")
    tmp.flush()
    tmp.close()
    return tmp.name


def test_load_contracteval_basic():
    tasks_data = [
        {"task_id": "HumanEval/1", "entry_point": "foo",
         "canonical_solution": "return 1", "canonical_solution_with_contract": "assert x>0\nreturn 1",
         "contract": "assert x>0", "contract_violating_test": [{"input": {"x": -1}}],
         "prompt": "def foo(x):\n"},
        {"task_id": "HumanEval/2", "entry_point": "bar",
         "canonical_solution": "return 2", "canonical_solution_with_contract": "return 2",
         "contract": "", "contract_violating_test": [],
         "prompt": "def bar():\n"},
    ]
    path = _make_test_jsonl(tasks_data)
    tasks = load_contracteval(path)
    assert len(tasks) == 2
    assert "HumanEval/1" in tasks
    assert tasks["HumanEval/1"]["entry_point"] == "foo"


def test_get_tasks_with_cvts():
    tasks_data = [
        {"task_id": "A", "entry_point": "a", "canonical_solution": "return 1",
         "canonical_solution_with_contract": "return 1", "contract": "",
         "contract_violating_test": [{"input": {"x": 1}}], "prompt": "def a():\n"},
        {"task_id": "B", "entry_point": "b", "canonical_solution": "return 2",
         "canonical_solution_with_contract": "return 2", "contract": "",
         "contract_violating_test": [], "prompt": "def b():\n"},
    ]
    path = _make_test_jsonl(tasks_data)
    tasks = load_contracteval(path)
    with_cvts = get_tasks_with_cvts(tasks)
    assert "A" in with_cvts
    assert "B" not in with_cvts


def test_get_z3_tractable_ids():
    tasks_data = [
        {"task_id": "A", "entry_point": "a", "canonical_solution": "return 1",
         "canonical_solution_with_contract": "return 1",
         "contract": "assert x > 0", "contract_violating_test": [], "prompt": "def a():\n"},
        {"task_id": "B", "entry_point": "b", "canonical_solution": "return 2",
         "canonical_solution_with_contract": "return 2",
         "contract": "", "contract_violating_test": [], "prompt": "def b():\n"},
    ]
    path = _make_test_jsonl(tasks_data)
    tasks = load_contracteval(path)
    tractable = get_z3_tractable_ids(tasks)
    assert "A" in tractable
    assert "B" not in tractable
