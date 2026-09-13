"""Tests for Gate Checker."""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from analysis.gate_checker import GateChecker


def test_gate_checker_init():
    """Test GateChecker initialization."""
    checker = GateChecker(
        primary_threshold=0.30,
        secondary_threshold=0.25,
        alpha=0.05
    )

    assert checker.primary_threshold == 0.30
    assert checker.secondary_threshold == 0.25
    assert checker.alpha == 0.05


def test_check_primary_gate_pass():
    """Test primary gate passes with sufficient correlation."""
    checker = GateChecker()

    result = checker.check_primary_gate(rho=0.35, p_value=0.01)

    assert result['passed'] == True
    assert result['rho_sufficient'] == True
    assert result['p_significant'] == True
    assert result['rho'] == 0.35
    assert result['threshold'] == 0.30


def test_check_primary_gate_fail_rho():
    """Test primary gate fails with insufficient ρ."""
    checker = GateChecker()

    result = checker.check_primary_gate(rho=0.20, p_value=0.01)

    assert result['passed'] == False
    assert result['rho_sufficient'] == False
    assert result['p_significant'] == True


def test_check_primary_gate_fail_p():
    """Test primary gate fails with non-significant p-value."""
    checker = GateChecker()

    result = checker.check_primary_gate(rho=0.35, p_value=0.10)

    assert result['passed'] == False
    assert result['rho_sufficient'] == True
    assert result['p_significant'] == False


def test_check_secondary_gate_pass():
    """Test secondary gate passes."""
    checker = GateChecker()

    result = checker.check_secondary_gate(partial_rho=0.28, partial_p=0.03)

    assert result['passed'] == True
    assert result['rho_sufficient'] == True
    assert result['p_significant'] == True


def test_determine_routing_pass():
    """Test routing decision for PASS."""
    checker = GateChecker()

    results = {
        'primary': {'passed': True, 'rho': 0.35, 'p_value': 0.01},
        'secondary': {'passed': True, 'rho': 0.28, 'p_value': 0.03}
    }

    routing = checker.determine_routing(results)

    assert routing['status'] == 'PASS'
    assert routing['route_to'] is None
    assert 'validated' in routing['recommendation'].lower()


def test_determine_routing_partial():
    """Test routing decision for PARTIAL (weak correlation)."""
    checker = GateChecker()

    results = {
        'primary': {'passed': False, 'rho': 0.15, 'p_value': 0.10},
        'secondary': {'passed': False, 'rho': 0.12, 'p_value': 0.15}
    }

    routing = checker.determine_routing(results)

    assert routing['status'] == 'PARTIAL'
    assert 'Phase 2A' in routing['route_to']
    assert 'weak correlation' in routing['recommendation'].lower()


def test_determine_routing_fail():
    """Test routing decision for FAIL (no correlation)."""
    checker = GateChecker()

    results = {
        'primary': {'passed': False, 'rho': 0.05, 'p_value': 0.50},
        'secondary': {'passed': False, 'rho': 0.03, 'p_value': 0.60}
    }

    routing = checker.determine_routing(results)

    assert routing['status'] == 'FAIL'
    assert 'Phase 2A' in routing['route_to']
    assert 'alternative mechanisms' in routing['recommendation'].lower()
