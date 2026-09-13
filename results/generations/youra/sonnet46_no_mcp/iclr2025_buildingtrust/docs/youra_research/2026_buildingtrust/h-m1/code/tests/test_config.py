import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import config


def test_required_cols_present():
    assert all(isinstance(c, str) for c in config.REQUIRED_COLS)
    assert "ECE" in config.REQUIRED_COLS
    assert "TruthfulQA_pct" in config.REQUIRED_COLS
    assert "MMLU_acc" in config.REQUIRED_COLS


def test_threshold_values():
    assert config.PRIMARY_THRESHOLD == 0.40
    assert config.INTERNAL_THRESHOLD == 0.30
    assert config.DISCRIMINANT_THRESHOLD == 0.20
    assert config.DECODING_INVARIANCE_THRESHOLD == 0.30


def test_figure_names_complete():
    assert len(config.FIGURE_NAMES) >= 5
    assert all(isinstance(k, str) and isinstance(v, str) for k, v in config.FIGURE_NAMES.items())


def test_paths_are_strings():
    assert isinstance(config.SCORE_MATRIX_PATH, str)
    assert isinstance(config.RESULTS_DIR, str)
    assert isinstance(config.FIGURES_DIR, str)


def test_bootstrap_params():
    assert config.N_BOOTSTRAP == 10_000
    assert config.BOOTSTRAP_SEED == 42
    assert config.MIN_MODELS == 25
