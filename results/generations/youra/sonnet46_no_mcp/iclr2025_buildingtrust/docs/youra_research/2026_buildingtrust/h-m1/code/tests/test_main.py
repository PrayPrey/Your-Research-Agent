import sys
import os
from pathlib import Path
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import config


def test_main_runs_without_error():
    from main import main
    result = main()
    assert isinstance(result, dict)
    assert "PASS" in result
    assert "primary_result" in result


def test_main_gate_pass_logged(caplog):
    import logging
    from main import main
    with caplog.at_level(logging.INFO):
        main()
    assert "PRIMARY GATE" in caplog.text


def test_main_all_outputs_created():
    from main import main
    main()
    results_json = Path(config.RESULTS_DIR) / "hm1_results.json"
    validation_md = Path(config.RESULTS_DIR).parent / "04_validation.md"
    assert results_json.exists(), f"Missing: {results_json}"
    assert validation_md.exists(), f"Missing: {validation_md}"
    for fname in config.FIGURE_NAMES.values():
        fig_path = Path(config.FIGURES_DIR) / fname
        assert fig_path.exists(), f"Missing figure: {fig_path}"
