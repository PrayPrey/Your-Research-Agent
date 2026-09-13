"""Tests for data_loader.py"""
import sys
import json
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pytest
from data_loader import (
    load_accuracy_differentials,
    load_contamination_estimates,
    build_analysis_vectors,
    validate_inputs,
    BENCHMARKS,
    MODEL_SIZES,
    LITERATURE_CONTAMINATION,
)


def make_results_matrix(tmp_path: Path) -> str:
    """Write a minimal valid results_matrix.json."""
    matrix = {}
    for m in MODEL_SIZES:
        matrix[m] = {
            "pile": {b: 0.3 for b in BENCHMARKS},
            "dedup": {b: 0.32 for b in BENCHMARKS},
        }
    p = tmp_path / "results_matrix.json"
    p.write_text(json.dumps(matrix))
    return str(tmp_path)


def test_load_accuracy_differentials(tmp_path):
    folder = make_results_matrix(tmp_path)
    diff = load_accuracy_differentials(folder)
    assert set(diff.keys()) == set(MODEL_SIZES)
    for m in MODEL_SIZES:
        assert set(diff[m].keys()) == set(BENCHMARKS)
        for b in BENCHMARKS:
            assert abs(diff[m][b] - 0.02) < 1e-9  # dedup(0.32) - pile(0.30)


def test_load_accuracy_differentials_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_accuracy_differentials(str(tmp_path))


def test_load_contamination_estimates_fallback(tmp_path):
    """Falls back to literature estimates when no H-M1 file exists."""
    cont = load_contamination_estimates(str(tmp_path))
    assert set(cont.keys()) == set(BENCHMARKS)
    assert abs(cont["hellaswag"] - LITERATURE_CONTAMINATION["hellaswag"]) < 1e-9


def test_load_contamination_estimates_from_file(tmp_path):
    data = {b: 0.1 * (i + 1) for i, b in enumerate(BENCHMARKS)}
    (tmp_path / "contamination_estimates.json").write_text(json.dumps(data))
    cont = load_contamination_estimates(str(tmp_path))
    assert abs(cont["mmlu"] - 0.1) < 1e-9


def test_build_analysis_vectors(tmp_path):
    acc_diff = {m: {b: 0.01 * (i + 1) for i, b in enumerate(BENCHMARKS)} for m in MODEL_SIZES}
    cont_est = {b: float(i) * 0.05 + 0.01 for i, b in enumerate(BENCHMARKS)}
    cont_rep, diff_flat, diff_matrix = build_analysis_vectors(acc_diff, cont_est)
    assert cont_rep.shape == (16,)
    assert diff_flat.shape == (16,)
    assert diff_matrix.shape == (4, 4)


def test_validate_inputs_passes():
    acc_diff = {m: {b: 0.01 for b in BENCHMARKS} for m in MODEL_SIZES}
    cont_est = {b: 0.05 for b in BENCHMARKS}
    validate_inputs(acc_diff, cont_est)  # should not raise


def test_validate_inputs_nan_raises():
    acc_diff = {m: {b: float("nan") if b == "mmlu" else 0.01 for b in BENCHMARKS} for m in MODEL_SIZES}
    cont_est = {b: 0.05 for b in BENCHMARKS}
    with pytest.raises(ValueError, match="NaN"):
        validate_inputs(acc_diff, cont_est)
