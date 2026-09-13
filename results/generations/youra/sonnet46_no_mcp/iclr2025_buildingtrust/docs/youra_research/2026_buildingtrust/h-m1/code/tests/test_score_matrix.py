import sys, os, json, tempfile
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import numpy as np
import pandas as pd
import score_matrix


def _write_lmeval_results(path: Path, accs: dict):
    path.mkdir(parents=True, exist_ok=True)
    payload = {"results": {k: {"acc,none": v} for k, v in accs.items()}}
    with open(path / "results_2026.json", "w") as f:
        json.dump(payload, f)


def test_load_lmeval_summary():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp)
        _write_lmeval_results(p, {"mmlu": 0.65, "truthfulqa_mc1": 0.55})
        summary = score_matrix.load_lmeval_summary(p)
        assert "mmlu" in summary
        assert abs(summary["mmlu"] - 0.65) < 1e-6


def test_load_lmeval_summary_missing_raises():
    with tempfile.TemporaryDirectory() as tmp:
        try:
            score_matrix.load_lmeval_summary(Path(tmp) / "nonexistent")
            assert False
        except FileNotFoundError:
            pass


def test_validate_matrix_pass():
    df = pd.DataFrame({
        "model_id": [f"m{i}" for i in range(25)],
        "ECE": np.random.rand(25),
        "TruthfulQA_pct": np.random.rand(25) * 100,
        "AdvGLUE_drop": np.random.rand(25),
        "Brier": np.random.rand(25),
        "ANLI_drop": np.random.rand(25),
        "MMLU_acc": np.random.rand(25),
        "HumanEval_pass1": np.random.rand(25),
    })
    assert score_matrix.validate_matrix(df) is True


def test_validate_matrix_too_few():
    df = pd.DataFrame({"model_id": ["m1"], "ECE": [0.1], "TruthfulQA_pct": [60.0], "AdvGLUE_drop": [0.05]})
    assert score_matrix.validate_matrix(df) is False


def test_validate_matrix_nan_in_gate():
    df = pd.DataFrame({
        "model_id": [f"m{i}" for i in range(25)],
        "ECE": [float("nan")] + [0.1] * 24,
        "TruthfulQA_pct": [60.0] * 25,
        "AdvGLUE_drop": [0.05] * 25,
    })
    assert score_matrix.validate_matrix(df) is False
