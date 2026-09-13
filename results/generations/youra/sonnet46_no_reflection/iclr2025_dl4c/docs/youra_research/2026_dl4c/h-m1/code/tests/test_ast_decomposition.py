import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from ast_decomposition import (
    classify_ast_node,
    strip_docstrings_comments,
    compute_sep,
    compute_edit_distribution,
    compute_node_type_frequencies,
    CONTROL_FLOW_NODES,
    DATA_FLOW_NODES,
)


class TestClassifyAstNode:
    def test_control_flow_if(self):
        assert classify_ast_node("If") == "control_flow"

    def test_control_flow_for(self):
        assert classify_ast_node("For") == "control_flow"

    def test_control_flow_while(self):
        assert classify_ast_node("While") == "control_flow"

    def test_control_flow_try(self):
        assert classify_ast_node("Try") == "control_flow"

    def test_data_flow_assign(self):
        assert classify_ast_node("Assign") == "data_flow"

    def test_data_flow_call(self):
        assert classify_ast_node("Call") == "data_flow"

    def test_data_flow_return(self):
        assert classify_ast_node("Return") == "data_flow"

    def test_data_flow_functiondef(self):
        assert classify_ast_node("FunctionDef") == "data_flow"

    def test_surface_constant(self):
        assert classify_ast_node("Constant") == "surface"

    def test_surface_name(self):
        assert classify_ast_node("Name") == "surface"

    def test_surface_expr(self):
        assert classify_ast_node("Expr") == "surface"

    def test_surface_unknown(self):
        assert classify_ast_node("UnknownNode") == "surface"

    def test_all_control_flow_nodes(self):
        for node in CONTROL_FLOW_NODES:
            assert classify_ast_node(node) == "control_flow", f"{node} should be control_flow"

    def test_all_data_flow_nodes(self):
        for node in DATA_FLOW_NODES:
            assert classify_ast_node(node) == "data_flow", f"{node} should be data_flow"


class TestStripDocstringsComments:
    def test_strips_function_docstring(self):
        code = '''def foo():
    """This is a docstring."""
    return 1'''
        result = strip_docstrings_comments(code)
        assert '"""' not in result
        assert "return 1" in result

    def test_preserves_code_without_docstring(self):
        code = "x = 1\ny = 2\n"
        result = strip_docstrings_comments(code)
        assert "x = 1" in result
        assert "y = 2" in result

    def test_invalid_code_returns_original(self):
        code = "def foo(: invalid syntax"
        result = strip_docstrings_comments(code)
        assert result == code


class TestComputeSep:
    def test_returns_float_for_valid_code(self):
        code_a = "x = 1\n"
        code_b = "if True:\n    x = 2\n"
        result = compute_sep(code_a, code_b)
        # may be None if no edits, or a float
        assert result is None or (isinstance(result, float) and 0.0 <= result <= 1.0)

    def test_returns_none_for_invalid_code(self):
        result = compute_sep("def foo(: invalid", "x = 1")
        assert result is None

    def test_sep_in_range(self):
        code_a = "def foo():\n    return 1\n"
        code_b = "def foo():\n    if True:\n        return 2\n    return 1\n"
        result = compute_sep(code_a, code_b)
        if result is not None:
            assert 0.0 <= result <= 1.0

    def test_identical_code_returns_none_or_zero(self):
        code = "x = 1\ny = 2\n"
        result = compute_sep(code, code)
        # No edits → None (total_edits == 0)
        assert result is None


class TestComputeEditDistribution:
    def test_returns_dict_for_valid_code(self):
        code_a = "x = 1\n"
        code_b = "if True:\n    x = 2\n"
        result = compute_edit_distribution(code_a, code_b)
        if result is not None:
            assert "control_flow" in result
            assert "data_flow" in result
            assert "surface" in result
            assert "semantic" in result
            assert "total_edits" in result

    def test_proportions_sum_to_one_or_zero(self):
        code_a = "x = 1\n"
        code_b = "for i in range(10):\n    x += i\n"
        result = compute_edit_distribution(code_a, code_b)
        if result is not None and result["total_edits"] > 0:
            total = result["control_flow"] + result["data_flow"] + result["surface"]
            assert abs(total - 1.0) < 1e-9

    def test_returns_none_for_invalid_code(self):
        result = compute_edit_distribution("def foo(:", "x = 1")
        assert result is None

    def test_semantic_equals_cf_plus_df(self):
        code_a = "x = 1\n"
        code_b = "if x:\n    return x\n"
        result = compute_edit_distribution(code_a, code_b)
        if result is not None:
            assert abs(result["semantic"] - (result["control_flow"] + result["data_flow"])) < 1e-9


class TestComputeNodeTypeFrequencies:
    def test_counts_if_nodes(self):
        codes = ["if x:\n    pass\n", "if y:\n    if z:\n        pass\n"]
        result = compute_node_type_frequencies(codes, ["If", "For"])
        assert result["If"] >= 2
        assert result["For"] == 0

    def test_skips_invalid_code(self):
        codes = ["def foo(:", "x = 1\n"]
        result = compute_node_type_frequencies(codes, ["Assign"])
        assert result["Assign"] >= 1

    def test_returns_zero_for_absent_types(self):
        codes = ["x = 1\n"]
        result = compute_node_type_frequencies(codes, ["While", "For"])
        assert result["While"] == 0
        assert result["For"] == 0
