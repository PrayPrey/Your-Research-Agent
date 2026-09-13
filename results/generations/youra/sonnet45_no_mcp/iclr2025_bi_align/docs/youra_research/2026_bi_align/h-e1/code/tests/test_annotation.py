"""
Tests for annotation interface and storage.
"""
import pytest
import pandas as pd
import sys
from pathlib import Path
import tempfile
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from annotation.storage import save_annotations, load_annotations


@pytest.fixture
def temp_output_dir():
    """Create temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def mock_annotations():
    """Create mock annotations data."""
    data = []
    for sample_id in range(100):
        for annotator_id in [1, 2, 3]:
            data.append({
                'sample_id': sample_id,
                'annotator_id': annotator_id,
                'judgment': sample_id % 2 == 0
            })
    return pd.DataFrame(data)


def test_save_annotations(temp_output_dir, mock_annotations):
    """Test saving annotations to CSV."""
    output_file = os.path.join(temp_output_dir, "annotations.csv")

    save_annotations(mock_annotations, output_file)

    assert os.path.exists(output_file), "Annotations file should be created"
    assert os.path.getsize(output_file) > 0, "Annotations file should not be empty"


def test_load_annotations(temp_output_dir, mock_annotations):
    """Test loading annotations from CSV."""
    output_file = os.path.join(temp_output_dir, "annotations.csv")

    # Save first
    save_annotations(mock_annotations, output_file)

    # Load back
    loaded = load_annotations(output_file)

    assert len(loaded) == len(mock_annotations), "Should load same number of annotations"
    assert list(loaded.columns) == list(mock_annotations.columns), "Should have same columns"


def test_save_load_roundtrip(temp_output_dir, mock_annotations):
    """Test save and load roundtrip preserves data."""
    output_file = os.path.join(temp_output_dir, "annotations.csv")

    # Save
    save_annotations(mock_annotations, output_file)

    # Load
    loaded = load_annotations(output_file)

    # Compare
    pd.testing.assert_frame_equal(
        loaded.sort_values(['sample_id', 'annotator_id']).reset_index(drop=True),
        mock_annotations.sort_values(['sample_id', 'annotator_id']).reset_index(drop=True)
    )


def test_save_creates_directories(temp_output_dir, mock_annotations):
    """Test that save_annotations creates necessary directories."""
    nested_path = os.path.join(temp_output_dir, "nested", "dir", "annotations.csv")

    save_annotations(mock_annotations, nested_path)

    assert os.path.exists(nested_path), "Should create nested directories"
