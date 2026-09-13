"""Tests for hypothesis_tests module."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
import pytest
from src.hypothesis_tests import (
    run_p1_p2_tests,
    apply_fdr_correction,
    evaluate_gate,
)


def test_p1_p2_direction_correct():
    focal = {
        "mmlu": {
            "Wikipedia (en)": {"beta": 0.5, "se": 0.1},
            "Books3": {"beta": 0.2, "se": 0.1},
        },
        "hellaswag": {
            "Wikipedia (en)": {"beta": 0.1, "se": 0.1},
            "Books3": {"beta": 0.4, "se": 0.1},
        },
    }
    result = run_p1_p2_tests(focal)
    assert result["P1"]["direction"] is True, "P1: wiki > books for MMLU"
    assert result["P2"]["direction"] is True, "P2: books > wiki for HellaSwag"


def test_p1_p2_direction_wrong():
    focal = {
        "mmlu": {
            "Wikipedia (en)": {"beta": 0.1, "se": 0.1},
            "Books3": {"beta": 0.5, "se": 0.1},
        },
        "hellaswag": {
            "Wikipedia (en)": {"beta": 0.5, "se": 0.1},
            "Books3": {"beta": 0.1, "se": 0.1},
        },
    }
    result = run_p1_p2_tests(focal)
    assert result["P1"]["direction"] is False
    assert result["P2"]["direction"] is False
    assert result["P1"]["passed"] is False
    assert result["P2"]["passed"] is False


def test_p1_p2_nan_handling():
    focal = {"mmlu": {}, "hellaswag": {}}
    result = run_p1_p2_tests(focal)
    assert result["P1"]["passed"] is False
    assert result["P2"]["passed"] is False


def test_apply_fdr_correction_p3_pass():
    import pandas as pd
    lrt_df = pd.DataFrame({
        "p_value": [0.001, 0.002, 0.6, 0.7, 0.8, 0.9],
    }, index=[f"pair{i}" for i in range(6)])
    lrt_df.index.name = "pair"
    result = apply_fdr_correction(lrt_df)
    assert result["p3_passed"] is True, "2 significant pairs → P3 passes"
    assert result["n_significant"] >= 2


def test_apply_fdr_correction_p3_fail():
    import pandas as pd
    lrt_df = pd.DataFrame({
        "p_value": [0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
    }, index=[f"pair{i}" for i in range(6)])
    lrt_df.index.name = "pair"
    result = apply_fdr_correction(lrt_df)
    assert result["p3_passed"] is False


def test_evaluate_gate_primary_pass():
    p1_p2 = {"P1": {"passed": True}, "P2": {"passed": True}}
    fdr = {"p3_passed": False, "n_significant": 0}
    gate = evaluate_gate(p1_p2, p1_p2, fdr)
    assert gate["status"] == "PRIMARY_PASS"
    assert gate["route"] == "PASS"


def test_evaluate_gate_secondary_pass():
    p1_p2 = {"P1": {"passed": False}, "P2": {"passed": False}}
    fdr = {"p3_passed": True, "n_significant": 2}
    gate = evaluate_gate(p1_p2, p1_p2, fdr)
    assert gate["status"] == "SECONDARY_PASS"
    assert gate["route"] == "PASS"


def test_evaluate_gate_minimum_pass():
    p1_p2 = {"P1": {"passed": True}, "P2": {"passed": False}}
    fdr = {"p3_passed": False, "n_significant": 0}
    gate = evaluate_gate(p1_p2, p1_p2, fdr)
    assert gate["status"] == "MINIMUM_PASS"
    assert gate["route"] == "EXPLORE"


def test_evaluate_gate_all_fail():
    p1_p2 = {"P1": {"passed": False}, "P2": {"passed": False}}
    fdr = {"p3_passed": False, "n_significant": 0}
    gate = evaluate_gate(p1_p2, p1_p2, fdr)
    assert gate["status"] == "ALL_FAIL"
    assert gate["route"] == "PIVOT"
