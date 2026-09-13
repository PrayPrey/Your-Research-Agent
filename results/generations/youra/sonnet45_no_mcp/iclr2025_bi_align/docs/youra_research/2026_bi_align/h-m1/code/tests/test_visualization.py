"""
Tests for visualization functions.
"""
import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path
import tempfile
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from visualization.plots import (
    plot_base_rate_comparison,
    plot_agreement_heatmap,
    plot_violation_distribution,
    plot_length_bias
)


@pytest.fixture
def temp_output_dir():
    """Create temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


def test_plot_base_rate_comparison(temp_output_dir):
    """Test base-rate comparison plot generation."""
    output_path = os.path.join(temp_output_dir, "base_rate.png")

    plot_base_rate_comparison(
        base_rate=0.45,
        threshold=0.40,
        p_value=0.023,
        output_path=output_path
    )

    assert os.path.exists(output_path), "Plot file should be created"
    assert os.path.getsize(output_path) > 0, "Plot file should not be empty"


def test_plot_agreement_heatmap(temp_output_dir):
    """Test agreement heatmap generation."""
    output_path = os.path.join(temp_output_dir, "heatmap.png")

    # Create mock pairwise kappa matrix
    pairwise_kappas = pd.DataFrame(
        [[1.0, 0.8, 0.75],
         [0.8, 1.0, 0.82],
         [0.75, 0.82, 1.0]],
        index=[1, 2, 3],
        columns=[1, 2, 3]
    )

    plot_agreement_heatmap(
        pairwise_kappas=pairwise_kappas,
        output_path=output_path
    )

    assert os.path.exists(output_path), "Plot file should be created"
    assert os.path.getsize(output_path) > 0, "Plot file should not be empty"


def test_plot_violation_distribution(temp_output_dir):
    """Test violation distribution plot generation."""
    output_path = os.path.join(temp_output_dir, "violations.png")

    # Create mock annotations
    data = []
    for sample_id in range(100):
        for annotator_id in [1, 2, 3]:
            data.append({
                'sample_id': sample_id,
                'annotator_id': annotator_id,
                'judgment': sample_id < 60  # 60% violations
            })
    annotations = pd.DataFrame(data)

    plot_violation_distribution(
        annotations=annotations,
        output_path=output_path
    )

    assert os.path.exists(output_path), "Plot file should be created"
    assert os.path.getsize(output_path) > 0, "Plot file should not be empty"


def test_plot_length_bias(temp_output_dir):
    """Test length bias plot generation."""
    output_path = os.path.join(temp_output_dir, "length_bias.png")

    # Create mock samples
    samples = pd.DataFrame({
        'id': range(500),
        'length_quartile': ['Q1'] * 125 + ['Q2'] * 125 + ['Q3'] * 125 + ['Q4'] * 125
    })

    # Create mock final labels
    final_labels = np.array([1] * 50 + [0] * 75 +  # Q1: 40% violations
                            [1] * 60 + [0] * 65 +  # Q2: 48% violations
                            [1] * 55 + [0] * 70 +  # Q3: 44% violations
                            [1] * 65 + [0] * 60)   # Q4: 52% violations

    plot_length_bias(
        samples=samples,
        final_labels=final_labels,
        output_path=output_path
    )

    assert os.path.exists(output_path), "Plot file should be created"
    assert os.path.getsize(output_path) > 0, "Plot file should not be empty"


def test_plots_create_directories(temp_output_dir):
    """Test that plot functions create necessary directories."""
    nested_path = os.path.join(temp_output_dir, "nested", "dir", "plot.png")

    plot_base_rate_comparison(
        base_rate=0.45,
        threshold=0.40,
        output_path=nested_path
    )

    assert os.path.exists(nested_path), "Should create nested directories"
