"""Tests for analyze_sft_lcb.py"""
import json
import tempfile
from pathlib import Path
import pytest
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from analyze_sft_lcb import check_gate, extract_lcb_hard_pass1


def test_check_gate_signal_void_confirmed():
    result = check_gate(0.35, threshold=0.60)
    assert result["signal_void_confirmed"] is True
    assert result["pass1"] == 0.35


def test_check_gate_signal_void_not_confirmed():
    result = check_gate(0.65, threshold=0.60)
    assert result["signal_void_confirmed"] is False


def test_check_gate_margin():
    result = check_gate(0.40, threshold=0.60)
    assert abs(result["margin"] - 0.20) < 1e-9


def test_extract_lcb_hard_pass1_direct():
    data = {"pass@1": 0.25}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        tmp = f.name
    assert extract_lcb_hard_pass1(tmp) == 0.25
    Path(tmp).unlink()


def test_extract_lcb_hard_pass1_nested():
    data = {"livecodebench": {"pass@1": 0.18}}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        tmp = f.name
    assert extract_lcb_hard_pass1(tmp) == 0.18
    Path(tmp).unlink()
