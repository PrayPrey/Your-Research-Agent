"""Tests for A-6 TrainingWrapper (run_training.py) - spec compliance tests."""

import os
import sys
import pandas as pd
import pytest

_CODE_DIR = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, _CODE_DIR)

from run_training import (
    check_logs_sufficient,
    validate_training_outputs,
    CONDITIONS,
    MIN_ROWS,
)


def _make_logs(tmpdir, n_rows):
    os.makedirs(tmpdir, exist_ok=True)
    for cond in CONDITIONS:
        rows = [{"step": i + 1, "reward_density": 0.7} for i in range(n_rows)]
        pd.DataFrame(rows).to_csv(
            os.path.join(tmpdir, f"reward_density_{cond}.csv"), index=False
        )


class TestCheckLogsSufficient:
    def test_returns_false_when_no_logs(self, tmp_path):
        sufficient, counts = check_logs_sufficient(str(tmp_path), min_rows=5000)
        assert sufficient is False
        assert all(v == 0 for v in counts.values())

    def test_returns_true_when_sufficient(self, tmp_path):
        _make_logs(str(tmp_path), n_rows=5000)
        sufficient, counts = check_logs_sufficient(str(tmp_path), min_rows=5000)
        assert sufficient is True
        assert all(v >= 5000 for v in counts.values())

    def test_returns_tuple_bool_dict(self, tmp_path):
        sufficient, counts = check_logs_sufficient(str(tmp_path), min_rows=5000)
        assert isinstance(sufficient, bool)
        assert isinstance(counts, dict)
        assert set(counts.keys()) == set(CONDITIONS)

    def test_counts_header_subtracted(self, tmp_path):
        _make_logs(str(tmp_path), n_rows=10)
        _, counts = check_logs_sufficient(str(tmp_path), min_rows=1)
        assert all(v == 10 for v in counts.values())


class TestValidateTrainingOutputs:
    def test_raises_on_insufficient_rows(self, tmp_path):
        _make_logs(str(tmp_path), n_rows=100)
        with pytest.raises(RuntimeError, match="Insufficient rows"):
            validate_training_outputs(str(tmp_path), expected_rows=5000)

    def test_passes_when_sufficient(self, tmp_path):
        _make_logs(str(tmp_path), n_rows=5000)
        valid, counts = validate_training_outputs(str(tmp_path), expected_rows=5000)
        assert valid is True
        assert all(v >= 5000 for v in counts.values())

    def test_returns_tuple(self, tmp_path):
        _make_logs(str(tmp_path), n_rows=5000)
        result = validate_training_outputs(str(tmp_path), expected_rows=5000)
        assert isinstance(result, tuple)
        assert len(result) == 2
