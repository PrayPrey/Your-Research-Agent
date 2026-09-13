"""Tests for gate evaluation."""
import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_evaluate_import():
    import evaluate
    assert evaluate is not None


def test_check_gate_pass():
    from evaluate import check_gate
    results = {
        'waterbirds': {'ami': 0.65, 'worst_purity': 0.82},
        'celeba': {'ami': 0.71, 'worst_purity': 0.90},
    }
    gate_pass, per_ds = check_gate(results)
    assert gate_pass is True
    assert per_ds['waterbirds']['dataset_pass'] is True


def test_check_gate_fail():
    from evaluate import check_gate
    results = {
        'waterbirds': {'ami': 0.3, 'worst_purity': 0.82},
        'celeba': {'ami': 0.71, 'worst_purity': 0.90},
    }
    gate_pass, per_ds = check_gate(results)
    assert gate_pass is False
    assert per_ds['waterbirds']['dataset_pass'] is False


def test_format_results_table():
    from evaluate import format_results_table
    results = {
        'waterbirds': {'ami': 0.65, 'worst_purity': 0.82, 'ami_pass': True, 'purity_pass': True, 'dataset_pass': True},
    }
    table = format_results_table(results)
    assert 'waterbirds' in table
    assert '0.6500' in table


def test_save_results(tmp_path):
    from evaluate import save_results
    results = {
        'waterbirds': {'ami': 0.65, 'worst_purity': 0.82, 'dataset_pass': True},
    }
    save_results(results, True, str(tmp_path))
    assert (tmp_path / 'overall_results.yaml').exists()
    assert (tmp_path / 'overall_results.json').exists()
