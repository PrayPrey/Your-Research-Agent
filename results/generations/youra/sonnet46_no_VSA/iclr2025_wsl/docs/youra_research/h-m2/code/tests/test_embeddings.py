"""Tests for embeddings.py — verify_orbit_var and shape contracts."""
import sys
import os
import pytest
import numpy as np

# Ensure h-m2 code on path
_CODE = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, os.path.abspath(_CODE))

from embeddings import verify_orbit_var, ORBIT_VAR_EXPECTED, ORBIT_VAR_TOL


def test_verify_orbit_var_pass():
    """Value within 20% tolerance should not raise."""
    verify_orbit_var(ORBIT_VAR_EXPECTED)


def test_verify_orbit_var_pass_boundary():
    """Boundary values should pass."""
    verify_orbit_var(ORBIT_VAR_EXPECTED * 0.80)
    verify_orbit_var(ORBIT_VAR_EXPECTED * 1.20)


def test_verify_orbit_var_fail_too_low():
    """Value far below expected should raise RuntimeError."""
    with pytest.raises(RuntimeError):
        verify_orbit_var(ORBIT_VAR_EXPECTED * 0.50)


def test_verify_orbit_var_fail_too_high():
    """Value far above expected should raise RuntimeError."""
    with pytest.raises(RuntimeError):
        verify_orbit_var(ORBIT_VAR_EXPECTED * 2.0)
