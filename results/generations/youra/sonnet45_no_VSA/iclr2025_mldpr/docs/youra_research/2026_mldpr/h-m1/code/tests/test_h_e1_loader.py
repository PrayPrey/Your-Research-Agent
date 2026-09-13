"""Tests for H-E1 Data Loader."""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data_loading.h_e1_loader import HE1DataLoader


def test_he1_loader_init():
    """Test HE1DataLoader initialization."""
    loader = HE1DataLoader("path/to/data.csv")
    assert loader.h_e1_path == Path("path/to/data.csv")


def test_load_dcs_scores_with_synthetic_data():
    """Test loading DCS_3 scores from CSV file."""
    # Create temporary CSV file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("repo_id,dcs_3_score,creation_date\n")
        f.write("owner/repo1,2.5,2022-01-01\n")
        f.write("owner/repo2,1.0,2022-02-01\n")
        f.write("owner/repo3,3.0,2022-03-01\n")
        temp_path = f.name

    try:
        loader = HE1DataLoader(temp_path)
        df = loader.load_dcs_scores()

        assert len(df) == 3
        assert list(df.columns) == ['repo_id', 'dcs_3_score', 't0_date']
        assert df['dcs_3_score'].tolist() == [2.5, 1.0, 3.0]
    finally:
        Path(temp_path).unlink()


def test_validate_dcs_data_valid():
    """Test validation of valid DCS data."""
    df = pd.DataFrame({
        'repo_id': [f'owner/repo{i}' for i in range(100)],
        'dcs_3_score': np.random.uniform(0, 3, 100),
        't0_date': pd.Timestamp('2022-01-01')
    })

    loader = HE1DataLoader("dummy_path")
    assert loader.validate_dcs_data(df) == True


def test_validate_dcs_data_small_sample():
    """Test validation fails for small sample."""
    df = pd.DataFrame({
        'repo_id': ['owner/repo1', 'owner/repo2'],
        'dcs_3_score': [1.0, 2.0],
        't0_date': pd.Timestamp('2022-01-01')
    })

    loader = HE1DataLoader("dummy_path")
    assert loader.validate_dcs_data(df) == False


def test_validate_dcs_data_out_of_range():
    """Test validation fails for out-of-range scores."""
    df = pd.DataFrame({
        'repo_id': [f'owner/repo{i}' for i in range(100)],
        'dcs_3_score': np.random.uniform(-1, 5, 100),  # Invalid range
        't0_date': pd.Timestamp('2022-01-01')
    })

    loader = HE1DataLoader("dummy_path")
    assert loader.validate_dcs_data(df) == False
