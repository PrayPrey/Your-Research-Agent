"""
Tests for main experiment runner.
"""
import pytest
import sys
from pathlib import Path
import tempfile
import os
import yaml

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import load_config, interpret_kappa
import pandas as pd


@pytest.fixture
def temp_config_dir():
    """Create temporary directory with config file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a minimal config file
        config = {
            'experiment': {
                'name': 'test-experiment',
                'hypothesis_id': 'h-test',
                'seed': 42
            },
            'sampling': {
                'sample_size': 100,
                'stratification_column': 'length_quartile',
                'n_quartiles': 4,
                'samples_per_quartile': 25
            },
            'annotation': {
                'n_annotators': 3,
                'violation_criteria': ['Criterion 1', 'Criterion 2']
            },
            'dataset': {
                'name': 'test/dataset',
                'subset': 'test',
                'split': 'train',
                'cache_dir': None
            },
            'hypothesis_test': {
                'null_hypothesis_threshold': 0.40,
                'alpha': 0.05,
                'alternative': 'greater',
                'confidence_level': 0.95
            },
            'statistical_analysis': {
                'kappa_threshold': 0.75,
                'kappa_interpretation': {
                    'poor': [0.00, 0.20],
                    'slight': [0.21, 0.40],
                    'fair': [0.41, 0.60],
                    'moderate': [0.61, 0.75],
                    'substantial': [0.76, 1.00]
                }
            },
            'outputs': {
                'data_dir': './data',
                'figures_dir': './outputs/figures',
                'results_file': './outputs/results.json',
                'report_file': './outputs/report.md',
                'samples_file': 'samples.csv',
                'annotations_file': 'annotations.csv',
                'final_labels_file': 'final_labels.csv'
            },
            'logging': {
                'level': 'INFO',
                'format': 'simple'
            }
        }

        config_path = os.path.join(tmpdir, 'config.yaml')
        with open(config_path, 'w') as f:
            yaml.dump(config, f)

        yield tmpdir, config_path


def test_load_config(temp_config_dir):
    """Test config loading."""
    tmpdir, config_path = temp_config_dir

    config = load_config(config_path)

    assert config['experiment']['name'] == 'test-experiment'
    assert config['sampling']['sample_size'] == 100
    assert config['annotation']['n_annotators'] == 3


def test_interpret_kappa(temp_config_dir):
    """Test kappa interpretation."""
    tmpdir, config_path = temp_config_dir
    config = load_config(config_path)

    assert interpret_kappa(0.10, config) == 'poor'
    assert interpret_kappa(0.30, config) == 'slight'
    assert interpret_kappa(0.50, config) == 'fair'
    assert interpret_kappa(0.70, config) == 'moderate'
    assert interpret_kappa(0.80, config) == 'substantial'


def test_main_requires_real_annotations(temp_config_dir, tmp_path):
    """Test that main.py raises error when annotations are missing (no mock fallback)."""
    from main import run_experiment

    tmpdir, config_path = temp_config_dir

    # Update config to use tmp_path for outputs
    config = load_config(config_path)
    config['outputs']['data_dir'] = str(tmp_path / 'data')
    config['outputs']['figures_dir'] = str(tmp_path / 'figures')
    config['outputs']['results_file'] = str(tmp_path / 'results.json')
    config['outputs']['report_file'] = str(tmp_path / 'report.md')

    updated_config_path = tmp_path / 'config.yaml'
    with open(updated_config_path, 'w') as f:
        yaml.dump(config, f)

    # Create minimal samples file
    (tmp_path / 'data').mkdir(parents=True, exist_ok=True)
    samples = pd.DataFrame({
        'id': range(10),
        'prompt': [f'Prompt {i}' for i in range(10)],
        'rejected_response': [f'Response {i}' for i in range(10)],
        'length_quartile': [i % 4 for i in range(10)]
    })
    samples.to_csv(tmp_path / 'data' / 'samples.csv', index=False)

    # Should raise FileNotFoundError when annotations are missing
    with pytest.raises(FileNotFoundError, match="Annotation file not found"):
        run_experiment(config_path=str(updated_config_path))
