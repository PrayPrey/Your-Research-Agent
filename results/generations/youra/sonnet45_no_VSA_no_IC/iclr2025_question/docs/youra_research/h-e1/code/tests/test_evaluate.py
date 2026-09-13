"""Test suite for evaluation metrics."""
import pytest
from eval.metrics import compute_auroc, compute_spearman, check_gate, compute_roc_data


def test_compute_auroc():
    """Verify AUROC computation."""
    # Perfect uncertainty (high for incorrect, low for correct)
    y_true = [0, 0, 1, 1]
    uncertainties = [0.1, 0.2, 0.8, 0.9]

    auroc = compute_auroc(y_true, uncertainties)
    assert 0.5 <= auroc <= 1.0
    assert auroc > 0.9  # Should be high for perfect separation


def test_compute_spearman():
    """Verify Spearman correlation."""
    uncertainties = [0.1, 0.3, 0.7, 0.9]
    incorrectness = [0, 0, 1, 1]

    rho = compute_spearman(uncertainties, incorrectness)
    assert -1.0 <= rho <= 1.0
    assert rho > 0.5  # Positive correlation expected


def test_check_gate_pass():
    """Verify gate check passes when threshold met."""
    auroc_scores = {
        "temp_scaling": 0.65,
        "conformal": 0.75,
        "mc_k1": 0.60
    }

    passed = check_gate(auroc_scores, threshold=0.70)
    assert passed is True


def test_check_gate_fail():
    """Verify gate check fails when threshold not met."""
    auroc_scores = {
        "temp_scaling": 0.65,
        "conformal": 0.68,
        "mc_k1": 0.60
    }

    passed = check_gate(auroc_scores, threshold=0.70)
    assert passed is False


def test_compute_roc_data():
    """Verify ROC data computation."""
    y_true = [0, 0, 1, 1]
    uncertainties = [0.1, 0.2, 0.8, 0.9]

    roc_data = compute_roc_data(y_true, uncertainties)

    assert "fpr" in roc_data
    assert "tpr" in roc_data
    assert "thresholds" in roc_data
    assert len(roc_data["fpr"]) > 0
