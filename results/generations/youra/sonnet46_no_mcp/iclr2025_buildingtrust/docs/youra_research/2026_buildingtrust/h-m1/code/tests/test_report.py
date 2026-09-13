import sys, os, json, tempfile
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import numpy as np
import pandas as pd
import report


def _make_gate_eval(passes=True):
    return {
        "PASS": passes,
        "results": [
            {"pair": ("ECE", "TruthfulQA_pct"), "rho": 0.52, "ci": (0.21, 0.74), "passes": passes},
            {"pair": ("ECE", "AdvGLUE_drop"), "rho": 0.48, "ci": (0.15, 0.71), "passes": passes},
        ],
    }


def _make_corr_df():
    return pd.DataFrame([
        {"x": "ECE", "y": "TruthfulQA_pct", "rho": 0.52, "ci_low": 0.21, "ci_high": 0.74, "p_value": 0.003},
        {"x": "ECE", "y": "AdvGLUE_drop", "rho": 0.48, "ci_low": 0.15, "ci_high": 0.71, "p_value": 0.007},
    ])


def test_write_results_json_creates_file():
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "04_results.json"
        score_df = pd.DataFrame({"model_id": ["m1"], "ECE": [0.1], "Brier": [0.05]})
        factor_results = {"loadings": [0.8, 0.7, 0.6, 0.5, 0.4], "variance_explained": 0.6, "kmo": 0.75, "congruence": 0.92}
        report.write_results_json(score_df, _make_corr_df(), factor_results, _make_gate_eval(), out)
        assert out.exists()
        data = json.loads(out.read_text())
        assert "gate_evaluation" in data
        assert "score_matrix" in data
        assert data["gate_evaluation"]["PASS"] is True


def test_write_results_json_gate_fail():
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "04_results.json"
        score_df = pd.DataFrame({"model_id": ["m1"], "ECE": [0.3]})
        factor_results = {"loadings": [], "variance_explained": None, "kmo": None, "congruence": None}
        report.write_results_json(score_df, _make_corr_df(), factor_results, _make_gate_eval(False), out)
        data = json.loads(out.read_text())
        assert data["gate_evaluation"]["PASS"] is False


def test_write_validation_md_creates_file():
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "04_validation.md"
        factor_results = {"loadings": [], "variance_explained": 0.6, "kmo": 0.75, "congruence": 0.92}
        loo_results = {"auc": 0.78, "auc_mmlu_only": 0.61}
        report.write_validation_md(_make_gate_eval(), _make_corr_df(), factor_results, loo_results, out)
        assert out.exists()
        content = out.read_text()
        assert "MUST_WORK" in content
        assert "PASS" in content
