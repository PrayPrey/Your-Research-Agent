"""Unit tests for src/findable.py"""
import os, sys
import pandas as pd
import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.findable import compute_findable_score, compute_f1_pid, compute_f2_metadata, compute_accessible_score


def make_cohort():
    return pd.DataFrame({
        "did": [1, 2, 3, 4],
        "fair_F": [0.0, 0.3, 0.6, 0.9],
        "fair_A": [0.2, 0.4, 0.6, 0.8],
        "fair_aggregate": [0.2, 0.4, 0.6, 0.8],
    })


def test_compute_findable_score_weighted_composite():
    cohort = make_cohort()
    result = compute_findable_score(cohort, f1_weight=0.25, f2_weight=0.50, f3_weight=0.25)
    assert "findable_score" in result.columns
    assert result["findable_score"].between(0, 1).all()


def test_compute_findable_score_binary_split():
    cohort = make_cohort()
    result = compute_findable_score(cohort, f1_weight=0.25, f2_weight=0.50, f3_weight=0.25)
    assert "high_findable" in result.columns
    assert set(result["high_findable"].unique()).issubset({0, 1})
    # About half should be high
    assert result["high_findable"].sum() >= 1


def test_compute_accessible_score_range():
    cohort = make_cohort()
    scores = compute_accessible_score(cohort)
    assert (scores >= 0).all() and (scores <= 1).all()


def test_compute_f1_pid_binary():
    cohort = make_cohort()
    f1 = compute_f1_pid(cohort)
    assert set(f1.unique()).issubset({0.0, 1.0})
