"""Tests for evaluator.py — spec compliance (no network calls)."""
import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import json
import pytest
import tempfile
from unittest.mock import patch
from evaluator import build_lm_eval_cmd, load_results


def test_build_lm_eval_cmd_basic():
    cmd = build_lm_eval_cmd("EleutherAI/pythia-6.9b", "step143000", "./results")
    # cmd[0] is the lm_eval binary path (may be absolute)
    assert "lm_eval" in cmd[0]
    assert "--model" in cmd
    assert "hf" in cmd
    assert "--output_path" in cmd
    assert "./results" in cmd


def test_build_lm_eval_cmd_limit():
    cmd = build_lm_eval_cmd("model", "rev", "./out", limit=50)
    assert "--limit" in cmd
    idx = cmd.index("--limit")
    assert cmd[idx + 1] == "50"


def test_build_lm_eval_cmd_no_limit():
    cmd = build_lm_eval_cmd("model", "rev", "./out")
    assert "--limit" not in cmd


def test_build_lm_eval_cmd_model_args():
    cmd = build_lm_eval_cmd("EleutherAI/pythia-6.9b", "step143000", "./out")
    model_args_idx = cmd.index("--model_args")
    model_args = cmd[model_args_idx + 1]
    assert "pretrained=EleutherAI/pythia-6.9b" in model_args
    assert "revision=step143000" in model_args
    assert "dtype=float16" in model_args


def test_load_results_valid():
    fake = {
        "results": {
            **{f"mmlu_subject_{i:02d}": {"acc,none": 0.4, "acc_stderr,none": 0.01} for i in range(57)},
            "hellaswag": {"acc,none": 0.6, "acc_norm,none": 0.65},
            "arc_easy": {"acc,none": 0.7},
            "arc_challenge": {"acc,none": 0.38, "acc_norm,none": 0.42},
        }
    }
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(fake, f)
        fname = f.name

    result = load_results(pathlib.Path(fname))
    assert "hellaswag" in result
    assert "arc_easy" in result
    assert len([k for k in result if k.startswith("mmlu_")]) == 57


def test_load_results_missing_key():
    fake = {"results": {"hellaswag": {"acc,none": 0.6}}}
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(fake, f)
        fname = f.name
    with pytest.raises(KeyError):
        load_results(pathlib.Path(fname))


def test_load_results_no_results_key():
    fake = {"something_else": {}}
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(fake, f)
        fname = f.name
    with pytest.raises(ValueError):
        load_results(pathlib.Path(fname))


def test_load_results_partial_mmlu():
    fake = {
        "results": {
            **{f"mmlu_subject_{i:02d}": {"acc,none": 0.4} for i in range(5)},  # only 5
            "hellaswag": {"acc,none": 0.6},
            "arc_easy": {"acc,none": 0.7},
            "arc_challenge": {"acc,none": 0.38},
        }
    }
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(fake, f)
        fname = f.name
    with pytest.raises(ValueError, match="partial"):
        load_results(pathlib.Path(fname))
