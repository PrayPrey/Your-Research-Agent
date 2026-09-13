import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ast_metric import (
    extract_semantic_ast,
    compute_ast_semantic_edit_distance,
    batch_ast_edit_distances,
    ZSSNode,
    SEMANTIC_NODE_TYPES,
)


def test_extract_semantic_ast_returns_module_root():
    code = "x = 1"
    tree = extract_semantic_ast(code)
    assert isinstance(tree, ZSSNode)
    assert tree.label == "Module"


def test_semantic_node_types_captured():
    code = "if True:\n    x = 1\nfor i in range(3):\n    pass"
    tree = extract_semantic_ast(code)
    labels = {n.label for n in tree.children}
    assert "If" in labels
    assert "For" in labels


def test_assign_captured():
    code = "x = 1"
    tree = extract_semantic_ast(code)
    labels = {n.label for n in tree.children}
    assert "Assign" in labels


def test_syntax_error_raises_value_error():
    with pytest.raises(ValueError):
        extract_semantic_ast("def f(: pass")


def test_identical_code_zero_distance():
    code = "def f():\n    return 1"
    assert compute_ast_semantic_edit_distance(code, code) == 0.0


def test_different_code_positive_distance():
    code_a = "if True:\n    x = 1"
    code_b = "for i in range(10):\n    x = i"
    dist = compute_ast_semantic_edit_distance(code_a, code_b)
    assert dist > 0


def test_syntax_error_returns_inf():
    dist = compute_ast_semantic_edit_distance("def f(: pass", "x = 1")
    assert dist == float("inf")


def test_batch_ast_edit_distances():
    ref = {"t1": "if True:\n    x = 1", "t2": "x = 1"}
    cand = {"t1": "for i in range(3):\n    pass", "t2": "x = 1"}
    result = batch_ast_edit_distances(ref, cand)
    assert "t1" in result
    assert "t2" in result
    assert result["t2"] == 0.0
    assert result["t1"] > 0


def test_batch_missing_key_skipped():
    ref = {"t1": "x = 1", "t2": "y = 2"}
    cand = {"t1": "x = 1"}
    result = batch_ast_edit_distances(ref, cand)
    assert "t1" in result
    assert "t2" not in result


def test_semantic_node_types_set():
    expected = {"If", "For", "While", "Try", "With", "Assign", "AugAssign", "Call", "Return"}
    assert expected == set(SEMANTIC_NODE_TYPES)
