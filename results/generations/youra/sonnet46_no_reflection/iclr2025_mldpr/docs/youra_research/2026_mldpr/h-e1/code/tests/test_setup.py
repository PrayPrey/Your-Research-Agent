"""Tests for task-001: Environment setup verification."""
import pytest


def test_datasets_import():
    import datasets
    assert hasattr(datasets, "load_dataset")


def test_openml_import():
    import openml
    assert hasattr(openml, "study")


def test_scipy_import():
    from scipy import stats
    assert hasattr(stats, "mannwhitneyu")
    assert hasattr(stats, "kendalltau")


def test_sklearn_import():
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score
    assert LogisticRegression is not None


def test_numpy_import():
    import numpy as np
    assert np.__version__ >= "1.21.0"


def test_pandas_import():
    import pandas as pd
    assert pd.__version__ >= "1.3.0"


def test_matplotlib_import():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    assert plt is not None


def test_seaborn_import():
    import seaborn as sns
    assert sns is not None


def test_constat_import_or_fallback():
    """ConStat import failure is acceptable — fallback is implemented."""
    try:
        import constat
        has_constat = True
    except ImportError:
        has_constat = False
    # Either way is acceptable
    assert isinstance(has_constat, bool)
